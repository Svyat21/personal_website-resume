## Сайт-резюме 
### Описание проекта
#### Это учебный проект, написан на основе [Мега-Учебник Flask](https://habr.com/ru/post/346306/)

**Здесь реализованы авторизация и регистрация пользователей, 
страница профиля, публикация сообщений, подписка на пользователей 
и их сообщения, страница для создания собственного резюме, разбивка
сообщений на страницы**
#
#### Развертывание приложения:

```pip install -r requirements.txt```

#### Создание миграции репозитория

```flask db init```

```flask db migrate -m "resume website"```

```flask db upgrade```

#### Запуск приложения

```flask run```