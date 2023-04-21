from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255)
    language = fields.CharField(max_length=255, default="en")
