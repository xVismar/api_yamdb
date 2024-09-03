"""Модуль импорта данных из CSV."""
from pandas import read_csv
from sqlalchemy import create_engine

CSV_FILE_PATH = 'api_yamdb/static/data/'
TABLE_DICT = {}

import_csv_arguments = {
    'titles_csv': ('titles.csv', 'titles',
                   {'description': '', 'genre': '', 'rating': ''}),
    'category_csv': ('category.csv', 'category',
                     TABLE_DICT),
    'genre_csv': ('genre.csv', 'genres',
                  TABLE_DICT),
    'genre_title_csv': ('genre_title.csv', 'title_genre',
                        TABLE_DICT),
    'comments_csv': ('comments.csv', 'review__comments',
                     TABLE_DICT),
    'review_csv': ('review.csv', 'reviews',
                   TABLE_DICT),
    'users_csv': ('users.csv', 'users',
                  TABLE_DICT),
}


def import_csv(engine, csv_file, table_name, default_values={}):
    """Импортирует данные из cvs файла в sql базу."""
    data = read_csv(csv_file)
    for column, default_value in default_values.items():
        if column not in data.columns:
            data[column] = default_value
    data.to_sql(table_name, engine, if_exists='replace', index=False)


engine = create_engine('sqlite:///api_yamdb/db.sqlite3')
for csv_file, table_name, default_values in import_csv_arguments.values():
    import_csv(engine, CSV_FILE_PATH + csv_file, table_name, default_values)
    print('Успешный импорт из файла ' + csv_file)
print('Импорт завершен!')
