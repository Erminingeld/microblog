# -*- coding: utf-8 -*-
from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    # id используется как первичный ключ
    # Каждому пользвателю в бд будет присвоено уникальное значение 
    id = db.Column(db.Integer, primary_key=True)
    # Поля user,email и password определяются как строки
    # а их длина указывается так,что бы бд могла оптимизировать их пространство
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # Расширение таблицы пользователей в бд(позволяет редактировать профиль)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Позволяет подписываться на других пользователей
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    # Метод repr сообщает python как печатать объекты этого класса
    def __repr__(self):
        return '<User {}>'.format(self.username)
    # Реализация метода хэширования пароля
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Добавляет логику которая генерирует URL-адреса аватара
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    # Подписаться
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    # Отписаться
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    # Проверяет наличие связей (подписки) между пользователями
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    # Создаёт единый запрос бд, позволяет отслеживать свои ичужие сообщения
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    # Функции генерации и проверки токена jwt
    # Первая функция генерирует токен JWT в виде строки(т.к jwt.encode() возвращает токен в виде последовательности байтов)
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
    # Метод проверки токена
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# Функция загрузчика пользвателя с индификаторами для (Flask-Login)
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)