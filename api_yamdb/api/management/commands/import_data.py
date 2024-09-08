import logging
import os
import sqlite3
from datetime import datetime

from pandas import read_csv
from django.conf import settings
from django.core.management.base import BaseCommand

logging.basicConfig(
    level=logging.INFO, format=('%(asctime)s - %(levelname)s - %(message)s')
)

SERIES_NAME = {'category': 'category_id', 'author': 'author_id'}
PATH_TABLE = (
    ('static/data/users.csv', 'reviews_user'),
    ('static/data/titles.csv', 'reviews_title'),
    ('static/data/category.csv', 'reviews_category'),
    ('static/data/genre.csv', 'reviews_genre'),
    ('static/data/genre_title.csv', 'reviews_genre_title'),
    ('static/data/review.csv', 'reviews_review'),
    ('static/data/comments.csv', 'reviews_comment'),
)
MESSAGE = 'Импорт из файла {path} в таблицу {table} осуществлен.'

DEFAULT_VALUES = {
    'password': 'default_password',
    'is_superuser': False,
    'is_staff': False,
    'is_active': True,
    'date_joined': datetime.now(),
    'is_registration_complete': True,
}


def set_default_values(data, defaults):
    for column, default in defaults.items():
        if column not in data.columns:
            data[column] = default
        else:
            data[column].fillna(default, inplace=True)


class Command(BaseCommand):

    help = (
        'Импорт данных из файлов: users.csv, titles.csv, category.csv, '
        'genre.csv, genre_title.csv, review.csv, comments.csv в БД'
    )

    def handle(self, *args, **kwargs):
        connection = sqlite3.connect(settings.DATABASES['default']['NAME'])
        for path, table in PATH_TABLE:
            try:
                data = read_csv(
                    os.path.join(settings.BASE_DIR, path), index_col=0
                )
                if table == 'reviews_user':
                    set_default_values(data, DEFAULT_VALUES)
                data.rename(columns=SERIES_NAME).to_sql(
                    table, connection, if_exists="append", index=False
                )
                logging.info(MESSAGE.format(table=table, path=path))
            except Exception as error:
                logging.error(error)
