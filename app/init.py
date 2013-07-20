# -*- coding: utf-8 -*-

from models import *


def create_tables():
    ResearchData.create_table()


if __name__ == '__main__':
    create_tables()
