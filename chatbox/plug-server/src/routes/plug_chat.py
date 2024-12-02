from flask import Blueprint, request, current_app, Response, jsonify
from mongoengine import ValidationError
from src.models import Plug, ContextItem, User, Message
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
)
import datetime
from src.helper import get_token_counter, get_qa_prompt
from src.database.sqlite import SQLiteConnection
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.tools import ToolMetadata, RetrieverTool, QueryEngineTool
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.vector_stores import ChromaVectorStore
from llama_index.agent import OpenAIAgent
from llama_index.llms import ChatMessage, OpenAI
from llama_index.chat_engine.simple import SimpleChatEngine
from llama_index.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
import json
import pytz
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.config.config import URL_PATH
from src.tools.order_tool import OrderTool

plug_chat = Blueprint("plug_chat", __name__,
                      url_prefix=f"{URL_PATH}/plug/api/v1/plug_chat")
flask_env = os.environ.get("FLASK_ENV")

MODELS = {"GPT4": "gpt-4", "GPT3.5": "gpt-4"}


@plug_chat.post("/follow_up")
@jwt_required()
def create_follow_ups():
    try:
        data = request.get_data(as_text=True)
        plug_id = request.headers.get('plugId')
        user_id = get_jwt_identity()

        if not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_200_OK
        if not data:
            return {"code": 400, "message": "Invalid message"}, HTTP_200_OK

        plug = Plug.objects(id=plug_id, userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST

        # setup token counter
        token_counter = get_token_counter(plug)

        llm = OpenAI(model=plug.model, temperature=0.3,
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
        plug.save()

        return {
            "code": 200,
            "message": "Created follow up questions successfully.",
            "data": json.loads(follow_up_qs),
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to create follow up questions",
                "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug_chat.post("")
@jwt_required()
def chat_complete():
    try:
        plug_id = request.headers.get('plugId')
        user_id = get_jwt_identity()
        body = request.json
        query = body.get("message", None)
        history = body.get("history", None)

        if not plug_id:
            return {"code": 400, "message": "Invalid plug id"}, HTTP_200_OK
        if not body:
            return {"code": 400, "message": "Invalid message"}, HTTP_200_OK

        plug = Plug.objects(id=plug_id, userId=user_id).first()
        if not plug:
            return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND

        if not plug.active:
            return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
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
            plugId=plug_id, isFile=True, structured=True, progress=100)

        for item in structured_context_items:
            table_schema_objs.append(SQLTableSchema(
                table_name=f"{str(plug_id)}/{SQLiteConnection.format_table_name(item.source)}", context_str=item.contextString))
            context_strs.append(item.contextString)

        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )

        llm = OpenAI(model="gpt-4o")
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
                    description="Useful for retrieving product informations in the store, always use if unsure"
                    "Must use a detailed question as input to the tool.",
                )
            ),
            OrderTool(
                metadata=ToolMetadata(
                    name="context_information",
                    description="Use this tool to help user order, adding products to user's cart order.",
                )
            ),
        ]
        # create agent
        llm = OpenAI(model=plug.model, temperature=0.3,
                     api_key=plug.userKey if plug.userKey else None)
        # llm = OpenAI(model='gpt-4', temperature=0.3,
        #              api_key=plug.userKey if plug.userKey else None)

        context_agent = OpenAIAgent.from_tools(
            tools=tools,
            max_function_calls=len(tools),
            llm=llm,
            # verbose=True if flask_env == "development" else False,
            verbose=True,
            system_prompt=plug.prompt
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
        response = context_agent.stream_chat(query, chat_history=chat_history)
        response_gen = response.response_gen

        def generate_response():
            for token in response_gen:
                yield token

            # update mongo db
            plug.updatedAt = datetime.datetime.now(pytz.UTC)
            plug.token += (token_counter.total_llm_token_count +
                           token_counter.total_embedding_token_count)

            plug.save()

        response = Response(generate_response(), content_type='text/plain')
        response.headers['X-Accel-Buffering'] = 'no'
        return response
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to complete chat", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR


@plug_chat.post("/iframe")
def chat_complete_iframe():
    try:

        res = []
        body = request.json
        plug_id = body.get("plugId", None)
        questions = body.get("questions", None)
        for question in questions:
            query = (f"""
            i'll give you question : 
            {question}
            then you answer me each question and i want  your output to be in format like this foreach question and nothing else.
            FOR EXAMPLE :
            {{"role":"assistant","content":"your answer"}}
            """)
            history = None
            plug = Plug.objects(id=plug_id).first()
            if not plug:
                return {"code": 404, "message": "Plug not found"}, HTTP_404_NOT_FOUND
            if not plug.active:
                return {"code": 400, "message": "Plug is not active"}, HTTP_400_BAD_REQUEST
            # setup token counter
            token_counter = get_token_counter(plug)

            # create index
            chroma_client = current_app.config['CHROMA_CLIENT']
            chroma_collection = chroma_client.get_collection(name=str(plug.id))
            vector_store = ChromaVectorStore(
                chroma_collection=chroma_collection)
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store)

            # get custom prompt template for agent
            vector_retriever = index.as_retriever(similarity_top_k=1)
            connection = current_app.config['SQLITE_CONNECTION']
            table_node_mapping = SQLTableNodeMapping(connection)
            table_schema_objs = []
            context_strs = []

            structured_context_items = ContextItem.objects(
                plugId=plug_id, isFile=True, structured=True, progress=100)

            for item in structured_context_items:
                table_schema_objs.append(SQLTableSchema(
                    table_name=f"{plug_id}/{SQLiteConnection.format_table_name(item.source)}",
                    context_str=item.contextString))
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
                        description="Useful for retrieving context information in general"
                                    "Must use a detailed question as input to the tool.",
                    )
                ),
                QueryEngineTool(
                    query_engine=query_engine,
                    metadata=ToolMetadata(
                        name="context_information_tabular",
                        description=f"Useful for retrieving specific context about these entities: {context_strs}"
                                    "Must use a detailed question as input to the tool.",
                    )
                ),
            ]
            # create agent
            llm = OpenAI(model=plug.model, temperature=0.3)
            context_agent = OpenAIAgent.from_tools(
                tools=tools,
                max_function_calls=len(tools),
                llm=llm,
                verbose=True if flask_env == "development" else False,
                system_prompt=plug.prompt
            )

            chat_history = []

            # chat with agent
            response = context_agent.chat(query)
            print(str(response))
            response_dict = json.loads(str(response))
            user_mess = Message(
                role="user",
                content=question
            )
            chat_message = Message(
                role=response_dict.get('role'),
                content=response_dict.get('content')
            )
            print(response_dict)
            res.append(user_mess)
            res.append(chat_message)
        return {
            "code": 200,
            "message": "ok",
            "data": [message.to_json() for message in res]
        }, HTTP_200_OK
    except ValidationError as e:
        return {"code": 400, "message": "Validation error", "error": str(e)}, HTTP_200_OK
    except Exception as e:
        return {"code": 500, "message": "Failed to complete chat", "error": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
