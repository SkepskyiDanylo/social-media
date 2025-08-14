# 🌍 Social Media API

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Docker Installation](#-docker-installation)
- [API Examples](#-api-examples)
- [API Documentation](#-api-documentation)
- [Translation](#-translation)
- [Email Verification](#-email-verification)
- [License](#-license)
- [Contact](#-contact)
---

## 🎯 Overview

Social Media API is a demonstration project, smaller in scale compared to [Airport-API](https://github.com/SkepskyiDanylo/airport-api), 
created as a test assignment on the [Mate Academy](https://mate.academy) platform. 
The project was completed in approximately 7 hours and showcases basic social media 
functionalities, including user profiles, posts, comments, and interactions. It serves as a 
practical example of REST API development and Django REST Framework usage.
---

### 📊 Project Structure

![Social Media API structure](readmefiles/structure.png)

---

## 🚀 Features

- 👤 User registration and authentication  
- 🔐 JWT authentication (SimpleJWT)  
- 📱 Post publishing, commenting and liking
- ✉️ Email notifications (account activation and password reset)  
- 🧑‍💻 Admin dashboard  
- 📄 Auto-generated API documentation (Swagger & ReDoc)  
- 📅 Delayed celery tasks

---

## 🛠️ Tech Stack

- Python 3.11+
- Django 5.2
- Django REST Framework
- PostgreSQL
- SimpleJWT
- Swagger / ReDoc
- Celery
- Celery Result Backend
- Redis
- Flower

---

## 🔐 Environment Variables

To run this project, you will need to add the following environment variables to your .env file

### Django:

`DEBUG`

`SECRET_KEY`

### SMTP:

`USE_EMAIL_VERIFICATION`

`SMTP_PASSWORD`

`SMTP_HOST`

`SMTP_PORT`

`SMTP_HOST_USER`

`SMTP_DEFAULT_FROM_EMAIL`

`FRONTEND_URL`

### Postgres:

`POSTGRES_PASSWORD`

`POSTGRES_USER`

`POSTGRES_DB`

`POSTGRES_HOST`

`POSTGRES_PORT`

`PGDATA`

### Celery:

`CELERY_BROKER_URL`

Example file with short explanation you can find in *[.env.sample](env.sample)*

---

## 🐳 Docker Installation

▶ [Fork](https://github.com/SkepskyiDanylo/social-media/fork) the repository

Create a `.env` file with the [required](#-environment-variables) environment variables

▶️ Build and start the containers:

```bash

docker-compose up --build
```

It will start:
 
 - Web django-drf on `:8000`
 - Celery worker
 - Redis server on `:6379`
 - Flower on `:5555`

▶️ To stop containers:

```bash

docker-compose down
```
---

## 🗄️ Project Structure

```
├── social_media/    # Posts, Comments, Profiles
├── user/            # User management, Registration, Login, Logout
├──social_media_api/
   ├── settings.py
   └──...
├── manage.py
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

---

## 🌐 API Examples

### 🔐 Register a New User

```https
POST /api/user/register/
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### 🎟 Create delayed Post

```https
POST /api/social-media/posts/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
Content-Type: application/json

{
  "content": "Some post text...",
  "scheduled_at": "YYYY-MM-DD"
}
```

Then add image:
```https
POST /api/social-media/posts/<id>/add-image/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
Content-Type: multipart/formdata

{
  "image": file
}
```

---

## 📄 API Documentation

You can see all `URIs` by starting the project and using:

- Swagger: [`/swagger/`](http://localhost:8000/swagger/)
- ReDoc: [`/redoc/`](http://localhost:8000/redoc/)

---

## 🔐 Authentication & Access

- JWT-based authentication via `djangorestframework-simplejwt`
- Permissions managed using `IsAuthenticated`, `IsAdmin`, `IsAdminOrAuthenticatedReadOnly` etc.
- Email-based account activation and password reset
- Reworked User model to use `email` instead of `username`
---

## ✉️ Email Verification

To be able to use password reset via email you have to set `USE_EMAIL_VERIFICATION` as `True` in [.env](#-environment-variables)

If `USE_EMAIL_VERIFICATION` is true, after registration email will be sent to user email to activate an email.

---

## 🌐 Translation

To add new messages to translation use `gettext` or `gettext_lazy`

1. After adding new messages:
    ```bash
   python manage.py makemessages -l ru
   python manage.py makemessages -l ua
   ```
   Then add translation to messages in `.po` files: [ua](locale/ua/LC_MESSAGES/django.po)
2. To add new language:
    ```bash
   python manage.py makemessages -l language
   ```
   Then add translation to new `.po` file

   Then add new language to [settings.py](social_media_api/settings.py)
    ```python
   ...
   LANGUAGES = [
    ("en", "English"),
    ("ua", "Ukrainian"),
    ("short_code", "Full name") # <- Add your language here
    ]
   ...
   ```
---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

For questions or feedback:

- Email: kol230305@gmail.com  
- Telegram: [@ViverTonick](https://t.me/ViverTonick)

---
