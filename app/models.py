# encoding: utf-8
"""
models.py
"""

from peewee import *


sqlite_db = SqliteDatabase('sq.db')

class SqliteModel(Model):
    class Meta:
        database = sqlite_db


class ResearchData(SqliteModel):
    datetime = DateTimeField(index=True)
    name = CharField(index=True)
    data_type = CharField(default="raw")
    data = DoubleField(null=True)
    class Meta:
        indexes = (
            (('datetime','name'), False),
            (('datetime','name', 'data_type'), True),
        )
        order_by = ('datetime',)


#state = ('raw', 'raw-1min', 'raw-10min', 'average-1hour', 'average-1day')
