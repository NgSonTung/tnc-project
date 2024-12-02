from mongoengine import Document, StringField


class LLM(Document):
    name = StringField(required=True, unique=True)
    description = StringField(required=True, default="")
    provider = StringField(required=True)
    meta = {"collection": "llm"}

    def to_json(self):
        return {
            "id": str(self.pk),
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
        }
