from mongoengine import Document, StringField, ObjectIdField, IntField, signals, BooleanField, ListField, DateTimeField, BinaryField
from bson import ObjectId
import os
import sys
import datetime
import pytz
import MapItemModel
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)
from database.sqlite import SQLiteConnection
from database.chromadb import ChromaClient


chroma_client = ChromaClient()
sqlite_connection = SQLiteConnection()

class ContextChunk(Document):
    id = ObjectIdField(primary_key=True, required=True, default=ObjectId)
    n = IntField()
    data = BinaryField()
    files_id = ObjectIdField()
    meta = {"collection": "contextItem.chunks"}

class ContextItem(Document):
    plugId = ObjectIdField(required=True)
    chunkSize = IntField()
    uploadDate = DateTimeField(
        required=True, default=datetime.datetime.now(pytz.UTC))
    length = IntField()
    source = StringField()
    isParent = BooleanField(default=False)
    isFile = BooleanField(required=True)
    progress = IntField(default=0)
    structured = BooleanField(default=False)
    contextString = StringField()
    fileType = StringField()
    isAllowCreateMap = BooleanField(default=False)
    summary = StringField()
    isMapImage = BooleanField(default=False)
    isMapCreated = BooleanField(default=None)
    urls = ListField()
    mapPointUrl = StringField(default=None)
    children = ListField(ObjectIdField())
    meta = {"collection": "contextItem.files"}

    def to_json(self):
        return {
            "id": str(self.pk),
            "isParent": self.isParent,
            "summary": self.summary,
            "structured": self.structured,
            "chunkSize": self.chunkSize,
            "length": self.length,
            "uploadDate": self.uploadDate.timestamp(),
            "source": self.source,
            "plugId": str(self.plugId),
            "isFile": self.isFile,
            "contextString": self.contextString,
            "mapPointUrl": self.mapPointUrl,
            "progress": self.progress,
            "urls": self.urls,
            "isAllowCreateMap": self.isAllowCreateMap,
            "isMapCreated": self.isMapCreated,
            "isMapImage": self.isMapImage,
            "fileType": self.fileType,
            "children": [str(child) for child in self.children]
        }

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                if document.structured:
                    table_name = SQLiteConnection.format_table_name(
                        document.source)
                    SQLiteConnection.delete_tables_by_name(
                        sqlite_connection, f'{document.plugId}/{table_name}')
                else:
                    if document.children and document.isParent:
                        ContextItem.objects(id__in=document.children).delete()
                    chroma_collection = chroma_client.get_collection(
                        name=str(document.plugId))
                    chroma_collection.delete(
                        where={"context_id": str(document.id)})
                    print(MapItemModel.MapItem.objects(contextBaseId=document.id))
                    MapItemModel.MapItem.objects(contextBaseId=document.id).delete()
            except:
                return


signals.post_delete.connect(
    ContextItem.post_delete_hook, sender=ContextItem)