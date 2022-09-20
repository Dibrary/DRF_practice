from flask import Flask
from flask_restful import abort, Api, fields, marshal_with, reqparse, Resource
from datetime import datetime
from models import MessageModel
import status
from pytz import utc


class MessageManager():
    last_id = 0
    def __init__(self):
        self.messages = {}

    def insert_message(self, message):
        self.__class__  .last_id += 1
        message.id = self.__class__.last_id
        self.messages[self.__class__.last_id] = message

    def get_message(self, id):
        return self.messages[id]

    def delete_message(self, id):
        del self.messages[id] # del로 사전형의 key-value를 제거할 수 있다.


message_fields = {
    'id': fields.Integer,
    'uri': fields.Url('message_endpoint'),
    'message': fields.String, # 각 key로 들어올 value의 자료형 명시.
    'duration': fields.Integer,
    'creation_date': fields.DateTime,
    'message_category': fields.String,
    'printed_times': fields.Integer,
    'printed_once': fields.Boolean
}


message_manager = MessageManager() # 객체 인스턴스 생성 1번만 한다.


class Message(Resource):
    def abort_if_message_doesnt_exist(self, id):
        if id not in message_manager.messages: # 찾는 데이터의 id를 가진 메시지가 없으면,
            abort(status.HTTP_404_NOT_FOUND, message="Message {0} doesn't exist".format(id))

    @marshal_with(message_fields)
    def get(self, id):
        self.abort_if_message_doesnt_exist(id)
        return message_manager.get_message(id)

    def delete(self, id):
        self.abort_if_message_doesnt_exist(id)
        message_manager.delete_message(id)
        return '', status.HTTP_204_NO_CONTENT

    @marshal_with(message_fields)
    def patch(self, id):
        self.abort_if_message_doesnt_exist(id)
        message = message_manager.get_message(id)
        # message는 이렇게 표현된다. <models.MessageModel object at 0x0000023B7FF69EE0> 즉, MessageModel 즉 models.py에서 정의한 객체.

        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str)
        parser.add_argument('duration', type=int)
        parser.add_argument('printed_times', type=int)
        parser.add_argument('printed_once', type=bool)
        args = parser.parse_args()
        if 'message' in args:
            message.message = args['message']
        if 'duration' in args:
            message.duration = args['duration']
        if 'printed_times' in args:
            message.printed_times = args['printed_times']
        if 'printed_once' in args:
            message.printed_once = args['printed_once']
        return message


class MessageList(Resource):
    @marshal_with(message_fields)
    def get(self):
        return [v for v in message_manager.messages.values()]
    '''
    get에서 message_fields로 
    {'id': <class 'flask_restful.fields.Integer'>, 
    'uri': <flask_restful.fields.Url object at 0x0000015F6FBBAE50>, 
    'message': <class 'flask_restful.fields.String'>, 
    'duration': <class 'flask_restful.fields.Integer'>, 
    'creation_date': <class 'flask_restful.fields.DateTime'>, 
    'message_category': <class 'flask_restful.fields.String'>, 
    'printed_times': <class 'flask_restful.fields.Integer'>, 
    'printed_once': <class 'flask_restful.fields.Boolean'>}
    들어온다. 
    '''

    @marshal_with(message_fields)
    def post(self):
        print("MessageList의 post", message_fields)
        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str, required=True, help='Message cannot be blank!') #
        parser.add_argument('duration', type=int, required=True, help='Duration cannot be blank!')
        parser.add_argument('message_category', type=str, required=True, help='Message category cannot be blank!')
        # 위 3개는 빈칸으로 넣을 수 없다.

        args = parser.parse_args()
        message = MessageModel(
            message=args['message'],
            duration=args['duration'],
            creation_date=datetime.now(utc),
            message_category=args['message_category']
            )
        message_manager.insert_message(message)
        return message, status.HTTP_201_CREATED
    '''
    post로
    {'id': <class 'flask_restful.fields.Integer'>, 
    'uri': <flask_restful.fields.Url object at 0x000001CE8FFD4FD0>, 
    'message': <class 'flask_restful.fields.String'>, 
    'duration': <class 'flask_restful.fields.Integer'>, 
    'creation_date': <class 'flask_restful.fields.DateTime'>, 
    'message_category': <class 'flask_restful.fields.String'>, 
    'printed_times': <class 'flask_restful.fields.Integer'>, 
    'printed_once': <class 'flask_restful.fields.Boolean'>}
    '''

app = Flask(__name__)
api = Api(app)
api.add_resource(MessageList, '/api/messages/')
api.add_resource(Message, '/api/messages/<int:id>', endpoint='message_endpoint')


if __name__ == '__main__':
    app.run(debug=True) # 배포할 때는 debug를 False로 해야 함.

'''
{
	"id":2,
	"message":"Hi There",
	"duration":22,
	"message_category":"Knowledge"
}
이렇게 보내도 들어가지고,
{
	"message":"Hi There",
	"duration":22,
	"message_category":"Knowledge"
} 이렇게 id가 없어도 들어가진다. (대신 id는 1로 들어가짐)
'''