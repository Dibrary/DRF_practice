
from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow() # Marshmallow는 Mashmallow와 Flask를 통합하는 래퍼클래스다.

class AddUpdateDelete():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

class Message(db.Model, AddUpdateDelete): # Message라는 모델 하나
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(250), unique=True, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    category = db.relationship('Category', backref=db.backref('messages', lazy='dynamic' , order_by='Message.message'))
    printed_times = db.Column(db.Integer, nullable=False, server_default='0')
    printed_once = db.Column(db.Boolean, nullable=False, server_default='false')

    def __init__(self, message, duration, category): # 생성자
        self.message = message
        self.duration = duration
        self.category = category

class Category(db.Model, AddUpdateDelete): # Category라는 모델 하나
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name): # 생성자
        self.name = name

class CategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('api.categoryresource', id='<id>', _external=True)
    messages = fields.Nested('MessageSchema', many=True, exclude=('category',)) # 필드 선언

class MessageSchema(ma.Schema):
    id = fields.Integer(dump_only=True) # dump_only가 True이면 읽기 전용이다.
    message = fields.String(required=True, validate=validate.Length(1)) # required가 True이면 not null이다.
    # validate는 최소 길이가 1이 되게 설정함.

    duration = fields.Integer()
    creation_date = fields.DateTime()
    category = fields.Nested(CategorySchema, only=['id', 'url', 'name'], required=True) # 필드 선언
    printed_times = fields.Integer()
    printed_once = fields.Boolean()
    url = ma.URLFor('api.messageresource', id='<id>', _external=True) #

    @pre_load
    def process_category(self, data):
        category = data.get('category')
        if category:
            if isinstance(category, dict):
                category_name = category.get('name')
            else:
                category_name = category
            category_dict = dict(name=category_name)
        else:
            category_dict = {}
        data['category'] = category_dict
        return data

