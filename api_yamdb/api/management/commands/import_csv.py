import logging
import sqlite3

from pandas import read_csv
from django.conf import settings
from django.core.management.base import BaseCommand

logging.basicConfig(
    level=logging.INFO, format=('%(asctime)s - %(levelname)s - %(message)s')
)

SERIES_NAME = {'category': 'category_id', 'author': 'author_id'}
MODEL_TABLE = {
    'user': 'users_user',
    'title': 'reviews_title',
    'category': 'reviews_category',
    'genre': 'reviews_genre',
    'genretitle': 'reviews_title',
    'review': 'reviews_review',
    'comment': 'reviews_comment',
}
MESSAGE = 'Импорт из файла {path} в таблицу {table} осуществлен.'


class Command(BaseCommand):
    help = 'Импорт данных из файла .csv в БД'

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Название таблицы в которую осуществляется импорт данных.',
        )
        parser.add_argument(
            'path',
            type=str,
            help='Путь к файлу из которого осуществляется импорт данных.',
        )

    def handle(self, *args, **kwargs):
        connection = sqlite3.connect(settings.DATABASES['default']['NAME'])
        model = kwargs['model'].lower()
        path_file = kwargs['path']
        try:
            data = read_csv(path_file, index_col=0)
            data.rename(columns=SERIES_NAME).to_sql(
                MODEL_TABLE[model], connection, if_exists="append", index=False
            )
            logging.info(
                MESSAGE.format(table=MODEL_TABLE[model], path=path_file)
            )
        except Exception as error:
            logging.error(error)
