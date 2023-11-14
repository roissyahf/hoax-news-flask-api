import datetime
from peewee import *

DATABASE = SqliteDatabase("hoaxorvalid.db")


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    email = CharField(unique=True)
    username = CharField()
    password = CharField()


class Beritahoax(BaseModel):
    text_new = CharField()
    hoax = IntegerField()


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Beritahoax, User], safe=True)
    DATABASE.close()
