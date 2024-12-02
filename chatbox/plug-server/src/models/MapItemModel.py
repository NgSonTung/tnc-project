from mongoengine import Document, StringField, ObjectIdField, IntField, signals, BooleanField, ListField, DateTimeField
import os
import sys
import datetime
import pytz

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)


class MapItem(Document):
    name = StringField()
    contextBaseId = ObjectIdField()
    userId = ObjectIdField()
    meta = {"collection": "MapItem.images"}

    def to_json(self):
        return {
            "id": str(self.pk),
            "name": self.name,
            "contenxtBaseId": str(self.contenxtBaseId)
        }

    @classmethod
    def post_delete_hook(self, sender, document, **kwargs):
        if kwargs.get('deleted', True):
            try:
                if document.contextBaseId:
                    self.delete(contenxtBaseId=document.contenxtBaseId)
            except:
                return


signals.post_delete.connect(
    MapItem.post_delete_hook, sender=MapItem)
