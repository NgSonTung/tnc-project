from mongoengine import Document, StringField


class Feature(Document):
    name = StringField(required=True, unique=True)
    description = StringField(required=True, default="")
    meta = {"collection": "feature"}

    def to_json(self):
        return {
            "id": str(self.pk),
            "name": self.name,
            "description": self.description,
        }
