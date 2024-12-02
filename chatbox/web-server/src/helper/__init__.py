import os
import os
import tiktoken
import math
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms import OpenAI
from llama_index import ServiceContext, set_global_service_context
from llama_index.embeddings import OpenAIEmbedding
from llama_index.prompts.prompts import QuestionAnswerPrompt
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import request, jsonify
from src.models import User, Message, Subscription
from src.constants.http_status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND, \
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from bson.objectid import ObjectId
from mongoengine import ValidationError, EmbeddedDocumentField, ListField, Document, EmbeddedDocumentListField
from urllib.parse import urlparse
from llama_index.storage.docstore.utils import doc_to_json
from urllib.parse import urlparse


def get_root_url(full_url):
    parsed_url = urlparse(full_url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    root_url = f"{scheme}://{netloc}"
    return root_url


def add_documents(docstore, nodes, context_id, allow_update=True) -> None:
    context_id_field = 'contextId'
    for node in nodes:
        if not allow_update and docstore.document_exists(node.node_id):
            raise ValueError(
                f"node_id {node.node_id} already exists. "
                "Set allow_update to True to overwrite."
            )
        node_key = node.node_id
        data = doc_to_json(node)

        data[context_id_field] = context_id

        docstore._kvstore.put(
            node_key, data, collection=docstore._node_collection)


def get_file_extension(filename):
    return os.path.splitext(filename)[1]


def split_list(original_list, n):
    return [original_list[i * n:(i + 1) * n] for i in range((len(original_list) + n - 1) // n)]


def get_token_counter(plug):
    token_counter = TokenCountingHandler(
        tokenizer=tiktoken.encoding_for_model("text-embedding-ada-002").encode)
    # token_counter.reset_counts()
    callback_manager = CallbackManager([token_counter])

    # set the global service_context
    embed_model = OpenAIEmbedding(
        embed_batch_size=500, mode='similarity')  # ada-002
    # llm = OpenAI(model=plug.model, temperature=0)
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model, callback_manager=callback_manager)
    set_global_service_context(service_context)
    return token_counter


def get_qa_prompt():
    custom_prompt = (
        "Given the following sections from the context information, answer the question with that information and tools. Either use tools or answer the query directly.\n"
        "Context information is below.\n"
        "==============================\n"
        "{context_str}\n"
        "==============================\n"
        "Message is below.\n"
        "{query_str}\n"
    )

    return QuestionAnswerPrompt(custom_prompt)


def role_restrict(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()  # Verify the JWT token in the request

                user_id = get_jwt_identity()
                user = User.objects(id=user_id).first()
                if user and user.role in allowed_roles:
                    return fn(*args, **kwargs)
                else:
                    return jsonify({"code": 403, "message": "Forbidden"}), HTTP_403_FORBIDDEN

            except Exception as e:
                return jsonify(
                    {"code": 500, "message": "Internal server error", "error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

        return wrapper

    return decorator


def model_restrict(model):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()  # Verify the JWT token in the request

                user_id = get_jwt_identity()
                user = User.objects(id=user_id).first()

                subscription = Subscription.objects(id=user.subscriptionId)

                if subscription and model in subscription.models:
                    return fn(*args, **kwargs)
                else:
                    return jsonify({"code": 403, "message": "Forbidden"}), HTTP_403_FORBIDDEN

            except Exception as e:
                return jsonify(
                    {"code": 500, "message": "Internal server error", "error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

        return wrapper

    return decorator


def feature_restrict(feature):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()  # Verify the JWT token in the request

                user_id = get_jwt_identity()
                user = User.objects(id=user_id).first()

                subscription = Subscription.objects(id=user.subscriptionId)

                if subscription and feature in subscription.features:
                    return fn(*args, **kwargs)
                else:
                    return jsonify({"code": 403, "message": "Forbidden"}), HTTP_403_FORBIDDEN

            except Exception as e:
                return jsonify(
                    {"code": 500, "message": "Internal server error", "error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

        return wrapper

    return decorator


def percent(num1, num2):
    if num1 == 0:
        return '0%'
    else:
        return '{:.2f}'.format(((num2 - num1) / num1) * 100).rstrip('0').rstrip('.') + '%'


def growth(num1, num2):
    if num1 == 0:
        return 0
    else:
        return round(((num2 - num1) / num1) * 100, 2)


class Controller:
    @staticmethod
    def get_all(model, req):
        try:
            page = int(req.args.get('page', 1))
            page_size = int(req.args.get('pageSize', 10))
            total_documents = model.objects.count()
            total_pages = math.ceil(total_documents / page_size)
            if page_size > 10:
                page_size = 30
            query = {}
            for property in req.args:
                if property in model._fields:
                    value = req.args.get(property)
                    if value != "":
                        query[property] = {"$in": [value]}
            documents = model.objects(
                **query).skip((page - 1) * page_size).limit(page_size)

            if not documents:
                return {"code": 404, "message": f"{model.__name__} not found"}, HTTP_404_NOT_FOUND

            data = [document.to_json() for document in documents]

            return {"code": 200, f"data": data, "page": page * 1, "page_size": page_size * 1,
                    "total_pages": total_pages * 1, "total_documents": total_documents * 1,
                    "message": f"{model.__name__}s retrieved successfully"}, HTTP_200_OK
        except Exception as e:
            return {"code": 500, f"message": f"Failed to get {model.__name__}",
                    "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR

    def get_by_id(model, req, id):
        try:
            if not ObjectId.is_valid(id):
                return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST

            document = model.objects(id=ObjectId(
                oid=id)).first()

            if not document:
                return {"code": 404, "message": f"{model.__name__} not found"}, HTTP_404_NOT_FOUND

            return {"code": 200, "data": document.to_json(),
                    "message": f"{model.__name__} retrieved successfully"}, HTTP_200_OK
        except Exception as e:
            return {"code": 500, f"message": f"Failed to get {model.__name__}",
                    "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR

    def update_by_id(model, req, id):
        try:
            if not ObjectId.is_valid(id):
                return {"code": 400, "message": "Invalid id"}, HTTP_400_BAD_REQUEST

            data = req.json

            document = model.objects(id=ObjectId(oid=id)).first()

            if not document:
                return {"code": 404, "message": f"{model.__name__} not found"}, HTTP_404_NOT_FOUND

            for field in data:
                if field in document._fields:
                    field_value = data[field]
                    if field_value:
                        if field == "messages":
                            messages = [Message(**message)
                                        for message in field_value]
                            document[field] = messages
                        else:
                            document[field] = field_value
            document.save()

            return {
                "code": 200,
                "data": document.to_json(),
                "message": f"{model.__name__} updated successfully."
            }, HTTP_200_OK

        except ValidationError as e:
            return {
                "code": 500,
                "message": "Validation error",
                "error": str(e)}, HTTP_400_BAD_REQUEST

        except Exception as e:
            return {
                "code": 500,
                "message": f"Failed to update {model.__name__}.",
                "error": str(e)
            }, HTTP_500_INTERNAL_SERVER_ERROR

    def create(model, req, ):
        try:
            data = req.json
            document = model(**data).save()

            return {
                "code": 201,
                "message": f"{model.__name__} added successfully.",
                "data": document.to_json()
            }, HTTP_201_CREATED

        except ValidationError as e:
            return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_400_BAD_REQUEST
        except Exception as e:
            return {"code": 500, "message": f"Failed to create {model.__name__}",
                    "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR

    def delete(model, id):
        try:
            document = model.objects(id=id).first()

            if not document:
                return {
                    "code": 404,
                    "message": f"{model.__name__} not found"
                }, HTTP_404_NOT_FOUND

            document.delete()
            return {
                "code": 200,
                "data": document.to_json(),
                "message": f"{model.__name__} deleted successfully."
            }, HTTP_200_OK

        except Exception as e:
            return {
                "code": 500,
                "message": f"Failed to delete {model.__name__}.",
                "error": str(e)
            }, HTTP_500_INTERNAL_SERVER_ERROR


def is_valid_base_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc and not parsed_url.query and not parsed_url.fragment:
        if not parsed_url.path.endswith('/'):
            return True
    return False


def dict_to_list_of_lists(my_dict):
    return [[key, value] for key, value in my_dict.items()]


def get_all_model_fields(model_class, prefix='', is_prefix=False):
    fields = []
    for field_name, field in model_class._fields.items():
        full_field_name = f"{prefix}{field_name}." if is_prefix else field_name
        if isinstance(field, EmbeddedDocumentField):
            fields.extend(get_all_model_fields(field.document_type, prefix=f"{full_field_name}"))
        elif isinstance(field, ListField) and isinstance(field.field, EmbeddedDocumentField):
            fields.extend(get_all_model_fields(field.field.document_type, prefix=f"{full_field_name}"))
        else:
            fields.append(full_field_name)
    return fields


def is_field_in_embedded_document(model_class, key_to_check):
    for field_name, field in model_class._fields.items():
        # Check if the field is an EmbeddedDocumentField
        if isinstance(field, EmbeddedDocumentField):
            if key_to_check in field.document_type._fields:
                return True
        # Check if the field is an EmbeddedDocumentListField
        elif isinstance(field, EmbeddedDocumentListField):
            if key_to_check in field.field.document_type._fields:
                return True
    return False