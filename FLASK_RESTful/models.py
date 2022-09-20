'''
단순 VO 객체와 같은 역할을 할 클래스
'''

class MessageModel:
    def __init__(self, message, duration, creation_date, message_category):

        self.id = 0
        self.message = message
        self.duration = duration
        self.creation_date = creation_date
        self.message_category = message_category
        self.printed_times = 0
        self.printed_once = False