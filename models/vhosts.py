from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('vhosts.db')

class BaseModel(Model):
    class Meta:
        database = db

class Vhost(BaseModel):
    address = TextField(unique = True)
    secondary_address = TextField(null = True)
    internal_ip = TextField()
    internal_port = TextField()

try:
    db.connect()
    db.create_tables([Vhost])
except:
    print('File già esistente')
