import urllib.parse
import pytz
import datetime
import gevent
import os
import src.database.mongodb as mongo
import time
import json
from flask import current_app
from src.config.config import URL_PATH, UPLOAD_FILES
from dotenv import load_dotenv
from src.routes.ws import progressUpdate
from flask_jwt_extended import jwt_required, get_jwt_identity
from llama_index import Document
from llama_index import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index import VectorStoreIndex
from llama_index.indices import SummaryIndex
from src.helper.crawl import ApifyActor
from src.helper import (
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
    HTTP_400_BAD_REQUEST
)
from src.models import (
    ContextItem,
    Plug,
    User,
    Subscription,
)
from src.services import (handler_create_map_point)
from mongoengine import ValidationError
from flask import Blueprint, request, current_app
from gridfs import GridFS
from mongoengine.connection import get_db

load_dotenv()
sqlite_path = os.environ.get('SQLITE_DB_PATH')
flask_env = os.environ.get("FLASK_ENV")
server_url = os.environ.get("URL_API_BE")
demo_context_base = Blueprint("demo_context_base", __name__,
                              url_prefix=f"{URL_PATH}/web/api/v1/demo/context_base")
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

        data: ContextItem = ContextItem.objects(id=ObjectId(id)).first()

        if is_website and not is_recording:
            time_out = 120
            max_pages = 20

            if flask_env == "production":
                web_hook_url = f"{server_url}/web/api/v1/websocket/notify"
            elif flask_env == "staging":
                web_hook_url = f"{server_url}/stage/web/api/v1/websocket/notify"
            else:
                web_hook_url = f"{server_url}/stage/web/api/v1/websocket/notify"
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

        summary_index = SummaryIndex.from_documents(documents)
        query_engine = summary_index.as_query_engine(
            response_mode="tree_summarize")
        summary_str = query_engine.query(
            "Summarize these documents in under 300 words, must have 1 title and 1 subtitle, respond in markdown format")

        # Update tokens,updatedAt, ...
        plug.client.origin = crawl_url
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

        else:
            progressUpdate(context_item=data.to_json(), progress=100, is_file=not is_website,
                           message='Website upload finished', room=room)

    except Exception as e:
        progressUpdate(context_item=data.to_json(), progress=-1, is_file=not is_website,
                       message=f'Document upload failed. Error: {str(e)}', room=room)
        ContextItem.objects(id=ObjectId(id)).delete()


@demo_context_base.post("website")
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

        plug: Plug = Plug.objects(
            id=plug_id, userId=user_id).first()

        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
        user: User = User.objects(id=user_id).first()
        subscription: Subscription = Subscription.objects(
            id=user.subscriptionId).first()
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

        existing_context_item: ContextItem = ContextItem.objects(
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
