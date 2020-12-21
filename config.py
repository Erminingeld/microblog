import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # Расширение flask-wtf использует SecretKey для защиты веб форм,так же он генерирует токены и подписи
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Принимает местоположение базы данных приложения
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # Отключает функцию,которая опавещает меня каждый раз когда в базе данныъ внесено изменение
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Данные сервера эл почты
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['susanl@example.com']
    LANGUAGES = ['ru', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    POSTS_PER_PAGE = 10

