# encoding: utf-8
"""
models.py
"""

from peewee import *


sqlite_db = SqliteDatabase('sq.db')

class SqliteModel(Model):
    class Meta:
        database = sqlite_db


class JmaTemp(SqliteModel):
    datetime = DateTimeField(index=True)
    temperature = DoubleField(null=True)
    data_type = CharField(default="raw")
    class Meta:
        indexes = (
            (('datetime', 'data_type'), True),
        )
        order_by = ('datetime',)


class ResearchTemp(SqliteModel):
    datetime = DateTimeField(index=True)
    temperature1 = DoubleField(null=True)
    temperature2 = DoubleField(null=True)
    data_type = CharField(default="raw")
    class Meta:
        indexes = (
            (('datetime', 'data_type'), True),
        )
        order_by = ('datetime',)


#state = ('raw', 'average-1min', 'average-10min', 'average-1hour', 'average-1day')