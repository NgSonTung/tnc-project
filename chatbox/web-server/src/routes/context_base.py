import math
import ast
import re
import urllib.parse
import pytz
import datetime
import gevent
import os
import src.database.mongodb as mongo
import mimetypes
import time
import json
import nomic
import csv
from src.database.sqlite import SQLiteConnection
from flask import current_app, send_file
from src.config.config import URL_PATH, UPLOAD_FILES
from dotenv import load_dotenv
from src.routes.ws import progressUpdate, statusUpdate
from flask_jwt_extended import jwt_required, get_jwt_identity
from llama_index.readers.schema.base import Document
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex, SummaryIndex
from llama_index.chat_engine.simple import SimpleChatEngine
from llama_index.llms import OpenAI
from src.helper.file_reader import FileReader
from src.helper.crawl import ApifyActor
from src.helper.trifatula import TrafilaturaWebReader
from src.helper import (
    get_file_extension,
    get_token_counter,
    is_valid_base_url,
    split_list,
    get_root_url
)
from bson.objectid import ObjectId
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    HTTP_401_UNAUTHORIZED
)
from src.models import (
    ContextItem,
    Plug,
    User,
    Subscription,
    MapPoint,
    MapItem
)
from src.services import (handler_create_map_point, delete_map_point)
from mongoengine import ValidationError, Q
from flask import Blueprint, request, current_app
from gridfs import GridFS
from gridfs.errors import NoFile
from mongoengine.connection import get_db
from bs4 import BeautifulSoup
from llama_index.node_parser import SentenceSplitter
from jwt import decode
from nomic import atlas, AtlasDataset
from io import BytesIO
import base64
load_dotenv()
server_url = os.environ.get("URL_API_BE")
sqlite_path = os.environ.get('SQLITE_DB_PATH')
flask_env = os.environ.get("FLASK_ENV")
context_base = Blueprint("context_base", __name__,
                         url_prefix=f"{URL_PATH}/web/api/v1/context_base")
files_collection_name = "contextItem"
mongo.create_db_connection()
fs = GridFS(get_db(), collection=files_collection_name)


def upload_documents(connection, id, plug, chroma_collection, formatted_file_name, documents, is_tabular,
                     is_website=False, apify_token=None, crawl_url=None, room='', is_recording=False, is_dom=False):
    try:
        def tranform_dataset_item(item):
            return Document(
                text=item.get("text"),
                extra_info={
                    "url": item.get("url"),
                    "context_id": str(id),
                },
            )

        data = ContextItem.objects(id=ObjectId(id)).first()

        if is_website and not is_recording:
            time_out = 120
            max_pages = 20

            if flask_env == "production":
                web_hook_url = f"{server_url}/web/api/v1/websocket/notify"
            elif flask_env == "staging":
                web_hook_url = f"{server_url}/stage/web/api/v1/websocket/notify"
            else:
                # web_hook_url = f"{server_url}/web/api/v1/websocket/notify"
                web_hook_url= "https://webaipilot.neoprototype.ca//web/api/v1/websocket/notify"

            reader = ApifyActor(apify_token)
            run_id = reader.start_run(
                actor_id="apify/website-content-crawler",
                run_input={
                    "startUrls": [{
                        "url": crawl_url
                    }],
                    # "maxConcurrency": 20,
                    # "clickElementsCssSelector": "[aria-expanded=\"true\"]",
                    # "dynamicContentWaitSecs": 20,
                    "initialConcurrency": 10,
                    "htmlTransformer": "none",
                    "maxCrawlDepth": 3,
                    "maxCrawlPages": max_pages,
                    "maxResults": max_pages,
                },
                memory_mbytes=4096,
                wait_secs=time_out,
                timeout_secs=time_out,
                webhooks=[{"event_types": ['ACTOR.RUN.CREATED', 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED',
                                           'ACTOR.RUN.TIMED_OUT', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.RESURRECTED',
                                           'ACTOR.BUILD.CREATED', 'ACTOR.BUILD.SUCCEEDED', 'ACTOR.BUILD.FAILED',
                                           'ACTOR.BUILD.TIMED_OUT', 'ACTOR.BUILD.TIMED_OUT'],
                           "request_url": web_hook_url,
                           "payload_template": '{"eventType": {{eventType}},"eventData": {{eventData}},"resource": {{resource}}, "room":' + f'"{room}",' + '"contextItem":' + f'{json.dumps(data.to_json())}' + "}"}])

            documents = reader.finish_run(
                run_id=run_id, wait_secs=time_out, dataset_mapping_function=tranform_dataset_item)

            for document in documents:
                url = document.metadata["url"]
                new_context_item = ContextItem(
                    source=url, plugId=ObjectId(plug.id), isFile=False, progress=100).save()
                data.children.append(new_context_item.id)
                data.urls.append(url)

        if not is_tabular:
            token_counter = get_token_counter(plug)

            vector_store = ChromaVectorStore(
                chroma_collection=chroma_collection)

            storage_context = StorageContext.from_defaults(
                vector_store=vector_store)

            if is_dom:
                progressUpdate(context_item=data.to_json(), progress=30,
                               is_file=not is_website, message='', room=room)
            else:
                progressUpdate(context_item=data.to_json(), progress=70,
                               is_file=not is_website, message='', room=room)

            split_documents = split_list(documents, 1000)
            for split_document in split_documents:
                VectorStoreIndex(split_document, storage_context=storage_context,
                                 show_progress=True if flask_env == "development" else False)

            plug.token += (token_counter.total_llm_token_count +
                           token_counter.total_embedding_token_count)

            summary_index = SummaryIndex.from_documents(split_documents[0])
            query_engine = summary_index.as_query_engine(
                response_mode="tree_summarize")
            summary_str = query_engine.query(
                "Summarize these documents in under 300 words, must have 1 title and 1 subtitle, respond in markdown format")

        else:
            context_string = f'This table gives information regarding: {documents[1]} from the document: {formatted_file_name}'
            documents[0].to_sql((f'{plug.id}/{formatted_file_name}'),
                                connection, if_exists='replace')
            data.contextString = context_string

            progressUpdate(context_item=data.to_json(), progress=70,
                           is_file=not is_website, message='', room=room)

            llm = OpenAI(model="gpt-4", temperature=0.3)
            chat_engine = SimpleChatEngine.from_defaults(llm=llm)
            summary_str = str(chat_engine.chat(
                f'Summarize this table in under 300 words, only the first 3 rows is given for reference but there are more rows: {documents[0].columns.tolist()}\n{documents[0].head(3)}, must have 1 title and 1 subtitle, respond in markdown format'))

        # Update tokens,updatedAt, ...
        plug.updatedAt = datetime.datetime.now(pytz.UTC)
        plug.save()

        # Update upload status to finished
        data.summary = str(summary_str)
        data.progress = 100
        data.save()

        time.sleep(1)

        if not is_website:
            progressUpdate(context_item=data.to_json(), progress=100, is_file=not is_website,
                           message='File upload finished', room=room)
            if plug.isAutoCreateMap:
                # Create map
                provider = "nomic"
                map_point = handler_create_map_point(
                    provider, plug.userId, plug, id, UPLOAD_FILES, fs=fs)
                # if map_point[1] == 200:
                #     data.isMapCreated = True
                #     data.save()
                #     statusUpdate(context_item=map_point[0]["data"], is_file=not is_website,
                #                    message='Create map finished', room=room, event='context_item_upload')
                # else:
                #     data.mapPointStatus = None
                #     statusUpdate(context_item=data.to_json(), is_file=not is_website,
                #                message='Create map failed', room=room, event='context_item_upload')

        else:
            progressUpdate(context_item=data.to_json(), progress=100, is_file=not is_website,
                           message='Website upload finished', room=room)

    except Exception as e:
        progressUpdate(context_item=data.to_json(), progress=-1, is_file=not is_website,
                       message=f'Document upload failed. Error: {str(e)}', room=room)
        ContextItem.objects(id=ObjectId(id)).delete()


@context_base.post("file/confirm")
@jwt_required()
def upload_confirm():
    try:
        user_id = get_jwt_identity()

        uploaded_file = request.files['file']
        name = request.form['name']
        plug_id = request.form['plug_id']
        supported_formats = ['.pdf', '.csv', '.xls', '.xlsx']
        tabular_formats = ['.xls', '.xlsx', '.csv']
        plug = Plug.objects(id=plug_id, userId=user_id).first()

        if not ObjectId.is_valid(plug_id) or not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_200_OK

        if not name or not uploaded_file:
            return {"code": 400, "message": "Missing body"}, HTTP_200_OK

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        if current_app.config['UPLOAD_FILES'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST

        file_suffix = get_file_extension(uploaded_file.filename)

        if file_suffix not in supported_formats:
            return {"code": 400, "message": "Unsupported file type"}, HTTP_400_BAD_REQUEST

        is_tabular = file_suffix in tabular_formats

        if is_tabular:
            context_item = ContextItem.objects(
                plugId=plug_id, isFile=True, structured=True, source=uploaded_file.filename).first()
            if context_item:
                return {
                    "code": 200,
                    "message": "File already existed.",
                    "data": {'exists': True}
                }, HTTP_200_OK

        return {
            "code": 200,
            "message": "File doesnt exist.",
            "data": {'exists': False}
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": "Failed to confirm", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.get("file/preview/<context_base_id>")
def file_preview(context_base_id):
    try:
        file = fs.get(ObjectId(context_base_id))
        mime_type, _ = mimetypes.guess_type(file.source)
        response = send_file(
            file,
            as_attachment=False,
            download_name=file.source,
            mimetype=mime_type,
        )
        return response
    except NoFile:
        return {"code": 404, "message": f"File not found"}, HTTP_404_NOT_FOUND
    except ValidationError as e:
        return {"code": 500, "message": f"Validation error, error: {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": f"Failed to retrieve item, error: {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.post("file")
@jwt_required()
def file_upload():
    # try:
        user_id = get_jwt_identity()
        uploaded_file = request.files['file']
        file_type = request.form['file_type']
        plug_id = request.form['plug_id']
        supported_formats = ['.pdf', '.csv', '.xls', '.xlsx']
        tabular_formats = ['.xls', '.xlsx', '.csv']
        allow_map_formats = ['csv', 'xls', 'xlsx', 'json']
        plug = Plug.objects(id=plug_id, userId=user_id).first()

        if not ObjectId.is_valid(plug_id) or not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_200_OK

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        if current_app.config['UPLOAD_FILES'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST

        file_length = request.content_length
        uploaded_file.seek(0, 0)
        if int(file_length) > int(current_app.config['MAX_CONTENT_LENGTH']):
            return {"code": 413, "message": "File too large"}, HTTP_413_REQUEST_ENTITY_TOO_LARGE

        user = User.objects(id=user_id).first()
        subscription = Subscription.objects(id=user.subscriptionId).first()
        feature_limit = subscription.featuresLimit
        upload_limit = [
            feature.limit for feature in feature_limit if feature.name == "upload files"]
        file_uploaded = ContextItem.objects(
            plugId=plug_id, isFile=True).count()
        file_suffix = get_file_extension(uploaded_file.filename)
        if upload_limit and file_uploaded == int(upload_limit[0]):
            return {"code": 400, "message": "You have reached the upload limit"}, HTTP_400_BAD_REQUEST
        if file_suffix not in supported_formats:
            return {"code": 400, "message": "Unsupported file type"}, HTTP_400_BAD_REQUEST

        is_tabular = file_suffix in tabular_formats

        # check exist & save to mongodb
        is_allow_create_map = True if file_type in allow_map_formats else False
        exists = False
        if is_tabular:
            context_item = ContextItem.objects(
                plugId=plug_id, isFile=True, structured=True, source=uploaded_file.filename).first()
            if context_item:
                context_item.progress = 0
                context_item.save()
                exists = True
                id = context_item.id

        if not exists:
            id = fs.put(uploaded_file, source=uploaded_file.filename, plugId=ObjectId(
                plug.id), isFile=True, length=file_length, structured=is_tabular, progress=0, fileType=file_type,
                isAllowCreateMap=is_allow_create_map)
            context_item = ContextItem.objects(id=ObjectId(id)).first()

        # format file name
        formatted_file_name = SQLiteConnection.format_table_name(
            uploaded_file.filename)
        try:
            progressUpdate(context_item=context_item.to_json(), progress=0, is_file=True,
                           message='File upload started', room=str(user.id))

            # get plug's chroma collection
            chroma_client = current_app.config['CHROMA_CLIENT']
            chroma_collection = chroma_client.get_collection(
                name=str(plug.id))

            # Set up the ChromaVectorStore and load the data:
            uploaded_file.seek(0)
            reader = FileReader()
            documents = reader.load_data(
                input_file=uploaded_file,
                file_suffix=file_suffix,
                metadata={
                    "file_name": uploaded_file.filename,
                    "context_id": str(id),
                    "plug_id": str(plug.id)
                },
                context_item=context_item,
                room=str(plug.id)
            )

            progressUpdate(context_item=context_item.to_json(), progress=50, is_file=True,
                           message='', room=str(user.id))

            connection = current_app.config['SQLITE_CONNECTION']

            # Start async upload
            gevent.spawn(upload_documents, connection, id, plug,
                         chroma_collection, formatted_file_name, documents, is_tabular=is_tabular, room=str(user.id))

        except Exception as e:
            ContextItem.objects(id=ObjectId(id)).delete()
            progressUpdate(context_item=context_item.to_json(), progress=-1, is_file=True,
                           message=f'File upload failed. Error: {str(e)}.', room=str(user.id))
            return {"code": 500, "message": f"Failed to upload file, error {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR

        return {
            "code": 200,
            "message": "File upload started.",
            "data": context_item.to_json()
        }, HTTP_200_OK
    # except ValidationError as e:
    #     return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    # except Exception as e:
    #     return {"code": 500, "message": "Failed to upload file", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.post("website")
@jwt_required()
def web_upload():
    try:
        user_id = get_jwt_identity()

        body = request.json
        plug_id = body.get("plug_id")
        name = body.get("name")
        data = body.get("content")

        try:
            result = urllib.parse.urlparse(data)
            all([result.scheme, result.netloc])
        except ValueError:
            return {"code": 400, "message": "Invalid URL"}, HTTP_400_BAD_REQUEST

        if not ObjectId.is_valid(plug_id) or not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_400_BAD_REQUEST
        if not data or not is_valid_base_url(data):
            return {"code": 400,
                    "message": "The input must be a valid base URL without a trailing slash"}, HTTP_400_BAD_REQUEST
        if not name:
            return {"code": 400, "message": "Missing body"}, HTTP_400_BAD_REQUEST

        plug = Plug.objects(
            id=plug_id, userId=user_id).first()

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        user = User.objects(id=user_id).first()
        subscription = Subscription.objects(id=user.subscriptionId).first()
        feature_limit = subscription.featuresLimit
        upload_limit = [
            feature.limit for feature in feature_limit if feature.name == "crawl website"]
        file_uploaded = ContextItem.objects(
            plugId=plug_id, isFile=False, isParent=True).count()
        if upload_limit and file_uploaded == int(upload_limit[0]):
            return {"code": 400, "message": "You have reached the upload limit"}, HTTP_400_BAD_REQUEST
        if current_app.config['CRAWL_WEBSITE'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST

        root_url = get_root_url(data)

        existing_context_item = ContextItem.objects(
            source=root_url, plugId=ObjectId(plug.id), isFile=False, isParent=True).first()

        # if url exists, overwrite
        if existing_context_item:
            # save file to mongodb
            ContextItem.objects(id=existing_context_item.id).delete()

        context_item = ContextItem(
            source=root_url, plugId=ObjectId(plug.id), isFile=False, isParent=True, children=[], urls=[]).save()
        id = context_item.id

        try:
            progressUpdate(context_item=context_item.to_json(), progress=0, is_file=False,
                           message='Web crawl started', room=str(user.id))

            # get plug's chroma collection
            chroma_client = current_app.config['CHROMA_CLIENT']
            chroma_collection = chroma_client.get_collection(
                name=str(plug.id))

            apify_token = current_app.config['APIFY_TOKEN']

            gevent.spawn(upload_documents, None, id, plug,
                         chroma_collection, None, None, False, True, apify_token, data, room=str(user.id))

        except Exception as e:
            ContextItem.objects(id=ObjectId(id)).delete()
            progressUpdate(context_item=context_item.to_json(), progress=-1, is_file=False,
                           message=f'Website upload failed. Error: {str(e)}.', room=str(user.id))
            return {"code": 500,
                    "message": f"Failed to upload website context, error {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR

        return {
            "code": 200,
            "message": "Website crawl started.",
            "data": context_item.to_json(),
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": "Failed to crawl website", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.post("api")
def api_upload():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return {"code": 401, "message": "Unauthorized"}, HTTP_401_UNAUTHORIZED

        body = request.json
        client_key = body.get("client_key")
        apis = body.get("apis")
        website_url = body.get("url")

        user_id = decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"]).get('sub')
        plug = Plug.objects(client__key=client_key,
                            userId=ObjectId(user_id)).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

        if current_app.config['CRAWL_WEBSITE'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST

        subscription = Subscription.objects(id=user.subscriptionId).first()
        feature_limit = subscription.featuresLimit
        upload_limit = [
            feature.limit for feature in feature_limit if feature.name == "crawl website"]
        file_uploaded = ContextItem.objects(
            plugId=plug.id, isFile=False, isParent=True).count()
        if upload_limit and file_uploaded == int(upload_limit[0]):
            return {"code": 400, "message": "You have reached the upload limit"}, HTTP_400_BAD_REQUEST

        embedded_documents = []
        mongo_documents = []

        root_url = get_root_url(website_url)

        existing_context_item = ContextItem.objects(
            source=root_url, plugId=ObjectId(plug.id), isFile=False, isParent=True).first()

        if not existing_context_item:
            existing_context_item = ContextItem(source=root_url, plugId=ObjectId(
                plug.id), isFile=False, isParent=True, children=[], urls=[]).save()

        progressUpdate(context_item=existing_context_item.to_json(), progress=0, is_file=True,
                       message='', room=str(user.id))

        connection = current_app.config['SQLITE_CONNECTION']
        chroma_client = current_app.config['CHROMA_CLIENT']
        chroma_collection = chroma_client.get_collection(name=str(plug.id))

        for api in apis:
            payload = api.get("payload")
            response = api.get("response")
            url = api.get("url")
            document_str = f"payload: {payload}; response: {response}; url: {url}"

            existing_child = ContextItem.objects(
                source=url, plugId=ObjectId(plug.id), isFile=False).first()
            # if url exists, overwrite
            if existing_child:
                mongo_documents.append(existing_child)
                existing_child.uploadDate = datetime.datetime.now(pytz.UTC)
                existing_child.save()
                # delete existing embedded documents before inserting new ones
                chroma_collection.delete(
                    where={"context_id": str(existing_child.id)})
                embedded_documents.append(Document(text=document_str, metadata={
                    "url": url, "context_id": str(existing_child.id)}))
            else:
                new_context_item = ContextItem(source=url, plugId=ObjectId(
                    plug.id), isFile=False, progress=100).save()
                mongo_documents.append(new_context_item)
                existing_context_item.children.append(new_context_item.id)
                existing_context_item.urls.append(url)
                embedded_documents.append(Document(text=document_str, metadata={
                    "url": url, "context_id": str(new_context_item.id)}))
        existing_context_item.save()

        gevent.spawn(upload_documents, connection, existing_context_item.id, plug, chroma_collection,
                     None, embedded_documents, is_tabular=False, is_website=True, room=str(user.id), is_recording=True)
        return {
            "code": 200,
            "message": "API upload started.",
            "data": [document.to_json() for document in mongo_documents],
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": "Failed to upload api", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.post("dom")
def dom_upload():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return {"code": 401, "message": "Unauthorized"}, HTTP_401_UNAUTHORIZED

        body = request.json
        client_key = body.get("client_key")
        doms = body.get("doms")

        user_id = decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"]).get('sub')
        plug = Plug.objects(client__key=client_key,
                            userId=ObjectId(user_id)).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND

        if current_app.config['CRAWL_WEBSITE'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST

        subscription = Subscription.objects(id=user.subscriptionId).first()
        feature_limit = subscription.featuresLimit
        upload_limit = [
            feature.limit for feature in feature_limit if feature.name == "crawl website"]
        file_uploaded = ContextItem.objects(
            plugId=plug.id, isFile=False, isParent=True).count()
        if upload_limit and file_uploaded == int(upload_limit[0]):
            return {"code": 400, "message": "You have reached the upload limit"}, HTTP_400_BAD_REQUEST

        embedded_documents = []

        root_url = get_root_url(doms[0].get("url"))

        existing_context_item = ContextItem.objects(
            source=root_url, plugId=ObjectId(plug.id), isFile=False, isParent=True).first()

        if not existing_context_item:
            existing_context_item = ContextItem(source=root_url, plugId=ObjectId(
                plug.id), isFile=False, isParent=True, children=[], urls=[]).save()

        progressUpdate(context_item=existing_context_item.to_json(), progress=0, is_file=True,
                       message='', room=str(user.id))

        connection = current_app.config['SQLITE_CONNECTION']
        chroma_client = current_app.config['CHROMA_CLIENT']
        chroma_collection = chroma_client.get_collection(name=str(plug.id))

        for dom in doms:
            dom_str = dom.get("dom")
            url = dom.get("url")

            soup = BeautifulSoup(dom_str, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            clean_text = soup.get_text()

            # split to text chunks
            text_parser = SentenceSplitter(chunk_size=1024)
            text_chunks = text_parser.split_text(clean_text)

            existing_child = ContextItem.objects(source=url, plugId=ObjectId(
                plug.id), isFile=False, isParent=False).first()

            if existing_child:
                chroma_collection.delete(
                    where={"context_id": str(existing_child.id)})
                existing_child.uploadDate = datetime.datetime.now(pytz.UTC)
            else:
                existing_child = ContextItem(source=url, plugId=ObjectId(
                    plug.id), isFile=False, progress=100)
                # if url exists, overwrite
                existing_context_item.urls.append(url)

            existing_context_item.save()
            existing_child.save()

            for t in text_chunks:
                document = Document(text=f"{t}, from url: {url}", metadata={
                    "url": url, "context_id": str(existing_child.id)})
                embedded_documents.append(document)
        try:
            gevent.spawn(upload_documents, connection, existing_context_item.id, plug, chroma_collection,
                         None, embedded_documents, is_tabular=False, is_website=True, room=str(user.id),
                         is_recording=True)
        except Exception as e:
            if not existing_context_item:
                ContextItem.objects(id=existing_child.id).delete()
            return {"code": 500, "message": f"Failed to upload file, error {str(e)}"}, HTTP_500_INTERNAL_SERVER_ERROR

        return {
            "code": 200,
            "message": "DOM upload started.",
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": "Failed to upload DOM", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.delete("/<context_base_id>")
@jwt_required()
def delete_context_item(context_base_id):
    try:
        plug_id = request.args.get("plug_id")

        user_id = get_jwt_identity()

        if not ObjectId.is_valid(plug_id) or not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_400_BAD_REQUEST
        if not ObjectId.is_valid(context_base_id):
            return {"code": 400, "message": "Invalid context item id"}, HTTP_400_BAD_REQUEST

        context_item = ContextItem.objects(
            id=ObjectId(context_base_id), plugId=plug_id).first()

        if not context_item:
            return {"code": 404, "message": "Context base item not found"}, HTTP_404_NOT_FOUND

        plug = Plug.objects(
            id=context_item.plugId, userId=user_id).first()

        if not plug:
            return {"code": 404, "message": "plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        if context_item.progress != 100:
            return {"code": 400, "message": "Item upload is in progress"}, HTTP_400_BAD_REQUEST

        # delete map
        if context_item.isFile:
            map_point = plug.mapsPoint.filter(
                contextBaseId=context_base_id).first()
            if map_point and not map_point.isImage:
                gevent.spawn(delete_map_point, "nomic",
                             map_point, plug, context_item)
            else:
                gevent.spawn(delete_map_point, "2gai",
                             map_point, plug, context_item)

        context_item.delete()
        return {
            "code": 200,
            "message": "Context base item deleted successfully.",
            "data": context_item.to_json(),
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 500, "message": "Validation error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"code": 500, "message": "Failed to delete context base item",
                "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.get("context_item/<plug_id>")
@jwt_required()
def get_context_base_by_id(plug_id):
    try:
        user_id = get_jwt_identity()
        if not ObjectId.is_valid(plug_id):
            return {"code": 400, "message": "Invalid plug id"}, HTTP_400_BAD_REQUEST

        plug = Plug.objects(id=plug_id, userId=user_id).first()

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        query = (Q(isFile=True) | (Q(isFile=False) & Q(isParent=True))) & Q(
            plugId=ObjectId(plug_id))
        uploaded_list = ContextItem.objects(query).order_by("-id")

        files = [file for file in uploaded_list if file.isFile]

        urls = [url for url in uploaded_list if not url.isFile]
        return {
            "code": 200,
            "message": "Context base items retrieved successfully.",
            "data": {
                "file": [context_item.to_json() for context_item in files],
                "url": [context_item.to_json() for context_item in urls],
            }
        }, HTTP_200_OK

    except Exception as e:
        return {"code": 500, "message": "Get context base error", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.post("/<string:provider>")
@jwt_required()
def upload_file_to_create_map(provider):
    try:
        route_parameter = ast.literal_eval(
            current_app.config['ROUTE_PARAMETER_ALLOWED'])
        if provider not in route_parameter:
            return {"code": 400, "message": "Invalid route parameter"}, HTTP_400_BAD_REQUEST
        user_id = get_jwt_identity()
        data = request.json
        index = data.get("index", None)
        plug_id = data.get("plugId", None)
        if not data:
            return {"code": 400, "message": "Missing body"}, HTTP_400_BAD_REQUEST
        context_base_id = data.get("contextBaseId", None)
        plug = Plug.objects(id=plug_id).first()
        map_point = handler_create_map_point(provider, user_id, plug, context_base_id,
                                             current_app.config['UPLOAD_FILES'], index, fs)
        return map_point
    except Exception as e:
        return {"code": 500, "message": f"Upload file to create map failed. {str(e)}",
                "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.get("/map/")
@jwt_required()
def get_map():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        plug_id, context_base_id = request.args.get(
            'plugId'), request.args.get('contextId')
        plug = Plug.objects(id=plug_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        if current_app.config['UPLOAD_FILES'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST
        map_point = plug.mapsPoint.filter(
            contextBaseId=context_base_id).first()
        if map_point.isImage:
            context_item = ContextItem.objects(id=context_base_id).first()

            file = GridFS(get_db(), collection="MapItem").get(
                ObjectId(context_item.mapPointUrl))
            mime_type, _ = mimetypes.guess_type("image.png")
            print(mime_type)
            file_data = file.read()
            blob_object = BytesIO(file_data)
            blob_data_base64 = base64.b64encode(
                blob_object.getvalue()).decode('utf-8')
            return {
                "code": 200,
                "message": "Get map successfully",
                "data": blob_data_base64
            }, HTTP_200_OK
        map_url = map_point.mapPointUrl
        return {
            "code": 200,
            "message": "Get map successfully",
            "data": map_url
        }, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to get map", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@context_base.delete("/<string:provider>/map/<context_base_id>")
@jwt_required()
def delete_map(provider, context_base_id):
    try:
        route_parameter = ast.literal_eval(
            current_app.config['ROUTE_PARAMETER_ALLOWED'])
        if provider not in route_parameter:
            return {"code": 400, "message": "Invalid route parameter"}, HTTP_400_BAD_REQUEST
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        if not user:
            return {"code": 404, "message": "User not found"}, HTTP_404_NOT_FOUND
        plug = Plug.objects(userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        if current_app.config['UPLOAD_FILES'] not in plug.features:
            return {"code": 400, "message": "This plug doesn't have that feature"}, HTTP_400_BAD_REQUEST
        map_point = plug.mapsPoint.filter(
            contextBaseId=context_base_id, provider=provider).first()
        context_item = ContextItem.objects(
            id=ObjectId(context_base_id)).first()
        if not map_point:
            return {"code": 404, "message": "Map not found"}, HTTP_404_NOT_FOUND
        gevent.spawn(delete_map_point, provider, map_point, plug, context_item)

        return {
            "code": 200,
            "message": "Deleting map",
        }, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to delete map", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
