
# Проект 9-го спринта API_YAMDB
###### @Яндекс Практикум
***


## О проекте
Разработка полноценного API с нуля для проекта YaMDB


## Использованные технологии
Основа проекта
Python
Django
Django Rest Famework



Полный перечень использованных библиотек и модулей можно посмотреть в файле `requirements.txt`
***
## Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email и username на эндпоинт /api/v1/auth/signup/.
2. YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
3. Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).
4. При желании пользователь отправляет PATCH-запрос на эндпоинт /api/v1/users/me/ и заполняет поля в своём профайле (описание полей — в документации).

## Пользовательские роли

- Аноним — может просматривать описания произведений, читать отзывы и комментарии.
- Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать отзывы и ставить оценку произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы; может редактировать и удалять свои отзывы и комментарии. Эта роль присваивается по умолчанию каждому новому пользователю.
- Модератор (moderator) — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
- Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- Суперюзер Django — обладет правами администратора (admin)




## Установка и запуск проекта

<details>
  <summary><b<strong>Установка и запуск</strong></b></summary>

### Как запустить проект:

1. Клонировать репозиторий и перейти в него в командной строке:
  ```bash
  git clone https://github.com/xVismar/api_yamdb.git
  ```

  ```bash
  cd api_yamdb
  ```

2. Создать и активировать виртуальное окружение:
  ```bash
  python -m venv venv
  ```
  ```bash
  . venv/Scripts/activate
  ```

3. Обновить установщик Python и установить зависимости из файла requirements.txt:
  ```bash
  python -m pip install --upgrade pip
  ```
  ```bash
  pip install -r requirements.txt
  ```

4. Выполнить миграции:
  ```bash
  python ./api_yamdb/manage.py migrate
  ```

5. Запустить проект:
  ```bash
  python ./api_yamdb/manage.py runserver
  ```

</details>

***

## Импорт данных из CSV файлов в базу данных

<details>
  <summary><b<strong>Использование импорта данных</strong></b></summary>

Для импорта данных в базу данных из CSV файлов, используйте команду `import_data`.     
Эта команда позволяет импортировать данные из следующих файлов:
```
users.csv    
titles.csv    
category.csv    
genre.csv     
genre_title.csv    
review.csv    
comments.csv
```

### Шаги для использования команды `import_data`     
***     
### Подготовьте CSV файлы
Убедитесь, что файлы `users.csv`, `titles.csv`, `category.csv`, `genre.csv`, `genre_title.csv`, `review.csv` и `comments.csv` находятся в директории `static/data/`.
<br></br>
### Запустите команду
Выполните следующую команду в терминале из корневой директории проекта:
```bash
python ./yatube_api/manage.py import_data
```
<br></br>
### Проверьте логирование
Команда `import_data` будет выводить информацию о процессе импорта в консоль.    
Убедитесь, что все данные были успешно импортированы.
<br></br>

### Пример структуры CSV файлов
```
users.csv
id,username,email,password,is_superuser,is_staff,is_active,date_joined,is_registration_complete
1,johndoe,johndoe@example.com,hashed_password,False,False,True,2023-01-01 00:00:00,True
```

```
titles.csv
id,name,year,description,category_id
1,Example Title,2023,Description of the title,1
```

```
category.csv
id,name,slug
1,Category Name,category-slug
```

```
genre.csv
id,name,slug
1,Genre Name,genre-slug
```

```
genre_title.csv
id,genre_id,title_id
1,1,1
```

```
review.csv
id,title_id,text,author_id,score,pub_date
1,1,Review text,1,5,2023-01-01 00:00:00
```

```
comments.csv
id,review_id,text,author_id,pub_date
1,1,Comment text,1,2023-01-01 00:00:00
```
<br></br>

### Примечания
Убедитесь, что все необходимые поля присутствуют в CSV файлах.    
Если какие-либо поля отсутствуют, команда `import_data` автоматически заполнит их значениями по умолчанию.    
В случае ошибок, информация об ошибках будет выведена в консоль.    
</details>




***
**Авторы** -

Алексеев Алексей (Vismar)    
Дамир Шарафетдинов (pretype)    
Никита Худяков (TrueDmitrich)    

_Студенты 11-когорты бэкенд-факультета   Яндекс Практикум_    
**Курс** - Python-разработчик буткемп    


07/09/2024 - Сдача первой работающей версии проекта    
08/09/2024 - Сдача второй версии проекта после правок Ревью 1
