import json
import pytz
import os
import datetime
from flask import Blueprint, request, current_app, Response
from mongoengine import ValidationError
from src.models import Message, Plug, Guest, History, ContextItem, User
from src.database.sqlite import SQLiteConnection
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
)
from src.helper import get_token_counter, get_qa_prompt, get_root_url
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.tools import ToolMetadata, RetrieverTool, QueryEngineTool
from llama_index.vector_stores import ChromaVectorStore
from llama_index.agent import OpenAIAgent
from llama_index.llms import ChatMessage, OpenAI
from llama_index.chat_engine.simple import SimpleChatEngine
from bson import ObjectId
from src.config.config import URL_PATH
from llama_index.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from src.tools.order_tool import OrderTool

client_chat = Blueprint("client_chat", __name__,
                        url_prefix=f"{URL_PATH}/plug/api/v1/client_chat")
flask_env = os.environ.get("FLASK_ENV")

MODELS = {"GPT4": "gpt-4", "GPT3.5": "gpt-4"}


@client_chat.post("/follow_up")
def create_follow_ups():
    try:
        data = request.get_data(as_text=True)
        client_key = request.headers.get('clientKey')

        if not client_key:
            return {"code": 400, "message": "Invalid client key"}, HTTP_200_OK
        if not data:
            return {"code": 400, "message": "Invalid message"}, HTTP_200_OK

        plug = Plug.objects(client__key=client_key).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        client = plug.client

        # if client.origin != '':
        #     request_origin = request.headers.get('Origin')
        #     if request_origin not in [client.origin, get_root_url(current_app.config['BASE_URL'])]:
        #         return {"code": 403, "message": "Unallowed domain"}, HTTP_403_FORBIDDEN

        # setup token counter
        token_counter = get_token_counter(plug)

        llm = OpenAI(model="gpt-4", temperature=0.3,
                     api_key=plug.userKey if plug.userKey else None)

        chat_engine = SimpleChatEngine.from_defaults(llm=llm)
        follow_up_qs = str(chat_engine.chat(
            f"""
            Based on this query: '{data}', give 3 follow up question suggestions, your output must always be in valid JSON format and nothing else.
            EXAMPLE OUTPUT:
            [
                "How does ocean pollution impact marine life?",
                "What can individuals do to help reduce ocean pollution?",
                "How does ocean pollution impact human life?",
            ]
            """,
        ))

        plug.token += (token_counter.total_llm_token_count +
                       token_counter.total_embedding_token_count)

        client.token += (token_counter.total_llm_token_count +
                         token_counter.total_embedding_token_count)
        plug.save()

        return {
            "code": 200,
            "message": "Created follow up questions successfully.",
            "data": json.loads(follow_up_qs),
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to create follow up questions", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@client_chat.post("")
def chat_complete_no_history():
    try:
        client_key = request.headers.get('clientKey')
        body = request.json
        data = body.get("message", None)
        history = body.get("history", None)

        if request.headers.getlist("X-Forwarded-For"):
            client_ip = request.headers.getlist(
                "X-Forwarded-For")[0].split(',')[0]
        else:
            client_ip = request.remote_addr
        if not client_key:
            return {"code": 400, "message": "Invalid client key"}, HTTP_200_OK
        if not body:
            return {"code": 400, "message": "Invalid message"}, HTTP_200_OK

        plug = Plug.objects(client__key=client_key).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        client = plug.client

        # if client.origin != '':
        #     request_origin = request.headers.get('Origin')
        #     if request_origin not in [client.origin, get_root_url(current_app.config['BASE_URL'])]:
        #         return {"code": 403, "message": "Unallowed domain"}, HTTP_403_FORBIDDEN

        # setup token counter
        token_counter = get_token_counter(plug)

        # create index
        chroma_client = current_app.config['CHROMA_CLIENT']
        chroma_collection = chroma_client.get_collection(name=str(plug.id))
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        # get custom prompt template for agent
        vector_retriever = index.as_retriever(similarity_top_k=1)
        connection = current_app.config['SQLITE_CONNECTION']
        table_node_mapping = SQLTableNodeMapping(connection)
        table_schema_objs = []
        context_strs = []

        structured_context_items = ContextItem.objects(
            plugId=plug.id, isFile=True, structured=True, progress=100)

        for item in structured_context_items:
            table_schema_objs.append(SQLTableSchema(
                table_name=f"{str(plug.id)}/{SQLiteConnection.format_table_name(item.source)}", context_str=item.contextString))
            context_strs.append(item.contextString)

        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )

        llm = OpenAI(model="gpt-4")
        service_context = ServiceContext.from_defaults(llm=llm)
        query_engine = SQLTableRetrieverQueryEngine(
            connection, obj_index.as_retriever(similarity_top_k=1), service_context=service_context
        )

        # create tools for agent
        tools = [
            RetrieverTool(
                retriever=vector_retriever,
                metadata=ToolMetadata(
                    name="context_information",
                    description="Useful for retrieving context information in general, always use if unsure"
                    "Must use a detailed question as input to the tool.",
                )
            ),
            OrderTool(
                metadata=ToolMetadata(
                    name="order_tool",
                    description="Use this tool to help user order products, adding products to user's cart order.",
                )
            ),
        ]

        # create agent
        llm = OpenAI(model=plug.model, temperature=0.3,
                     api_key=plug.userKey if plug.userKey else None)
        context_agent = OpenAIAgent.from_tools(
            tools=tools,
            max_function_calls=len(tools),
            llm=llm,
            verbose=True,
            system_prompt=plug.prompt,
        )

        chat_history = []

        if history:
            # get chat history
            for message in history:
                chat_history.append(ChatMessage(
                    role=message.get('role'),
                    content=message.get('content')
                ))

        # chat with agent
        response = context_agent.stream_chat(data, chat_history=chat_history)
        response_gen = response.response_gen

        has_feature = current_app.config['SAVE_CONVERSATION'] in plug.features

        def generate_response():
            response_text = ""
            for token in response_gen:
                yield token
                response_text += token

            tokens = token_counter.total_llm_token_count + \
                token_counter.total_embedding_token_count

            # update mongo db
            plug.updatedAt = datetime.datetime.now(pytz.UTC)
            plug.token += tokens
            client.token += tokens
            plug.save()

            if has_feature:
                guest = Guest.objects(client=ObjectId(
                    client.id), ip=client_ip).first()
                print(guest)
                if guest:
                    history = History.objects(guest=ObjectId(
                        guest.id)).order_by('-id').first()

                    history.updatedAt = datetime.datetime.now(pytz.UTC)

                    Message.objects.insert([Message(content=data, role="user", history=history.id, createdAt=datetime.datetime.now(pytz.UTC)),
                                            Message(content=response_text, role='assistant', history=history.id, createdAt=datetime.datetime.now(pytz.UTC))])


                    history.save()

        response = Response(generate_response(), content_type='text/plain')
        response.headers['X-Accel-Buffering'] = 'no'
        return response
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to complete chat", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@client_chat.post("/history")
def create_history():
    try:
        client_key = request.headers.get('clientKey')
        if request.headers.getlist("X-Forwarded-For"):
            client_ip = request.headers.getlist(
                "X-Forwarded-For")[0].split(',')[0]
        else:
            client_ip = request.remote_addr

        if not client_key:
            return {"code": 400, "message": "Invalid client key"}, HTTP_200_OK

        plug = Plug.objects(client__key=client_key).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        client = plug.client

        # if client.origin != '':
        #     request_origin = request.headers.get('Origin')
        #     if request_origin not in [client.origin, get_root_url(current_app.config['BASE_URL'])]:
        #         return {"code": 403, "message": "Unallowed domain"}, HTTP_403_FORBIDDEN

        guest = Guest.objects(client=ObjectId(
            client.id), ip=client_ip).first()

        if current_app.config['SAVE_CONVERSATION'] in plug.features:
            if guest:
                history = History.objects(
                    guest=guest.id).order_by('-id').first()
                if history:
                    messages = Message.objects(history=history.id)
                    if not messages:
                        return {"code": 400, "message": "Empty history already exists"}, HTTP_400_BAD_REQUEST
                History(guest=guest.id).save()
            else:
                guest = Guest(client=ObjectId(client.id), ip=client_ip).save()
                History(guest=guest.id).save()
        else:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST
        return {
            "code": 200,
            "message": "Created history successfully.",
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to complete chat", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
