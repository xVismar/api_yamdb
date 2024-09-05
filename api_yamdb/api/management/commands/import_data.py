import datetime
import logging
import os
import sqlite3

from pandas import read_csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User

logging.basicConfig(
    level=logging.INFO, format=('%(asctime)s - %(levelname)s - %(message)s')
)

SERIES_NAME = {'category': 'category_id', 'author': 'author_id'}
PATH_TABLE = (
    ('static/data/users.csv', 'users_user'),
    ('static/data/titles.csv', 'reviews_title'),
    ('static/data/category.csv', 'reviews_category'),
    ('static/data/genre.csv', 'reviews_genre'),
    ('static/data/genre_title.csv', 'reviews_title_genre'),
    ('static/data/review.csv', 'reviews_review'),
    ('static/data/comments.csv', 'reviews_comment'),
)
MESSAGE = 'Импорт из файла {path} в таблицу {table} осуществлен.'


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
                if table == 'users_user':
                    data['password'] = make_password('default_password')
                    data['is_superuser'] = False
                    if data.get('admin'):
                        data['is_staff'] = True
                    else:
                        data['is_staff'] = False
                    data['is_active'] = True
                    data['date_joined'] = datetime.datetime.today()
                    data['last_name'] = None
                    data['first_name'] = None
                    
                    # Assuming 'User' model has the same fields as 'users_user' table
                    User.objects.bulk_create(
                        [User(**row) for row in data.to_dict(orient='records')]
                    )
                logging.info(MESSAGE.format(table=table, path=path))
            except Exception as error:
                logging.error(error)