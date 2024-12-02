import datetime
import os
import sys
import pytz
from bson.objectid import ObjectId
from mongoengine import Document, StringField, DateTimeField, IntField, ObjectIdField, \
    ListField, signals, BooleanField, EmbeddedDocumentField, EmbeddedDocument, EmbeddedDocumentListField

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)
from database.chromadb import ChromaClient
sys.path.append(os.path.abspath(os.path.join('src', 'models')))
from GuestModel import Guest
from ContextItemModel import ContextItem
from ClientModel import Client

chroma_client = ChromaClient()

ROLES = ["system", "user", "assistant", "function"]

MODEL_CHOICES = ["gpt-4", "llama2", "gpt-4"]

FEATURE_DICT = {"crawl website": "crawlWebsite", "save conversation": "saveConversation",
                "upload files": "uploadFiles", "api access": "apiAccess", "customize client": "customizeClient",
                "custom WebAI Pilot plug": "custom2gaiplug", "llama 2 model": "llama2"}

MODEL_DICT = {"gpt-4": "gpt4",
              "gpt-4": "gpt3", "llama2": "llama2"}


class MapPoint(EmbeddedDocument):
    url = StringField(required=True, default="")
    name = StringField(required=True, default="")
    points = IntField(required=True, default=0)
    provider = StringField(required=True, default="nomic")
    isImage = BooleanField(default=False)
    contextBaseId = ObjectIdField(required=True)
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    updatedAt = DateTimeField(default=datetime.datetime.now(pytz.UTC))

    def to_json(self):
        return {
            "url": self.url,
            "name": self.name,
            "points": self.points,
            "createdAt": self.createdAt.timestamp(),
            "updatedAt": self.updatedAt.timestamp()
        }


class Plug(Document):
    plugName = StringField()
    userKey = StringField()
    model = StringField(required=True, choices=MODEL_CHOICES,
                        default="gpt-4")
    features = ListField(StringField(), default=[])
    token = IntField(required=True, default=0)
    createdAt = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    updatedAt = DateTimeField(default=datetime.datetime.now(pytz.UTC))
    liveDemo = BooleanField(default=False)
    prompt = StringField()
    client = EmbeddedDocumentField(Client, default=None)
    active = BooleanField(default=True)
    userId = ObjectIdField()
    isAutoCreateMap = BooleanField(default=False)
    mapsPoint = EmbeddedDocumentListField(MapPoint, default=[])
    meta = {
        "collection": "plug",
        'indexes': ['client.key']
    }

    def __init__(self, *args, **kwargs):
        super(Plug, self).__init__(*args, **kwargs)

        self.prompt = f"""\
                You always call a tool to retrieve more context information at least once\
                You are a very enthusiastic assistant developed by WebPilotAI who loves to help people!\
                You are powered by the {self.model} LLM model\
                You are using the api key { f"have last four digits {self.userKey[-4:]}" if self.userKey else "provided by WebPilotAI"}\
                Do not make up an answer if you don't know or the context information is not helpful."""

    def to_json(self):
        return {
            "id": str(self.pk),
            "plugName": self.plugName,
            "model": {MODEL_DICT.get(self.model): True},
            "features": {FEATURE_DICT.get(feature): True for feature in self.features if
                         FEATURE_DICT.get(feature) is not None},
            "token": self.token,
            "createdAt": self.createdAt.timestamp(),
            "updatedAt": self.updatedAt.timestamp(),
            "client": self.client.to_json() if self.client is not None else None,
            "active": self.active,
            "liveDemo": self.liveDemo,
            "userId": str(self.userId),
            "isAutoCreateMap": self.isAutoCreateMap,
            "mapsPoint": [mapPoint.to_json() for mapPoint in self.mapsPoint] if self.mapsPoint else None,
        }

    @classmethod
    def post_insert_hook(self, sender, document, **kwargs):
        if kwargs.get('created', True):
            try:
                from llama_index.vector_stores.chroma import ChromaVectorStore
                from llama_index import StorageContext
                from llama_index import Document
                from llama_index import VectorStoreIndex
                documents = [Document(text="""WebPilotAI's frequently asked questions:
                    -What is WebPilotAIPlug(™)?
                        WebPilotAIPlug(™) is a software product that seamlessly integrates with existing applications to provide Generative AI features.
                        WebPilotAIPlug will modernize applications by enabling Generative AI features out-of-box, with no additional cost or development required. It will support advanced functionalities like Natural Language Queries (NLQs), Information Extraction, Sentiment Analysis, and enhanced Customer Experience, empowering users to unlock the full potential of their applications. This seamless integration paves the way for a future of unprecedented efficiency, insights, and creativity.
                    -Where is my data stored?
                        At WebPilotAI, we prioritize the security of your data, which is why we only store the content on secure and encrypted AWS servers. We cannot read or access your documents. As part of higher plans you have the option to store the data in your own cloud environments
                    -What data formats are supported?
                        You have the flexibility to upload multiple file types, paste text, insert a URL. Using the Non-Invasive data ingestion means we can ingest text, images and live APIs
                    -Can I give WebPilotAIPlug(™) instructions?
                        You can customize the base prompt, give your chatbot a name, add personality traits, and even set instructions for answering questions in a fun and creative way.
                    -How can I add WebPilotAIPlugClient(™) to my website?
                        Transform your website with WebPilotAIPlug(™). Adding it is easy: simply train your custom AI model and choose whether you want to embed an iframe or add a chat bubble to the bottom right of your website.
                    -How can I Integrate WebPilotAIPlug(™) with other platforms?
                        WebPilotAIPlug(™) powerful API allows you to communicate with your custom AI model from anywhere, giving you ultimate flexibility.
                    -What are invasive and non-invasive modes in WebPilotAIPlug(™)?
                        Non-invasive mode: Collects API calling data, learns from input data, and provides Generative AI features like natural language queries and customer usage patterns.
                        Invasive mode: Configured based on the application's internal component architecture, allowing in-context learning at runtime and offering comprehensive Generative AI capabilities""",
                                      extra_info={
                                          "name": "WebPilot.AI's frequently asked questions",
                                      }, )]
                chroma_collection = chroma_client.create_collection(
                    name=str(document.id))
                vector_store = ChromaVectorStore(
                    chroma_collection=chroma_collection)
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store)
                VectorStoreIndex.from_documents(
                    documents, storage_context=storage_context)
            except:
                return

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                # Delete chroma item
                chroma_client.delete_collection(str(document.id))
                # Delete context item
                ContextItem.objects(
                    plugId=ObjectId(document.id)).delete()
                # Delete guest
                Guest.objects(client=document.id).delete()
            except:
                return


signals.post_save.connect(Plug.post_insert_hook, sender=Plug)
signals.post_delete.connect(Plug.post_delete_hook, sender=Plug)
