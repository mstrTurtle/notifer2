from dataclasses import dataclass
from datetime import datetime

# 一些用来给shelves用的。直接dataclass因为shelves保存的是对象。Python的对象是动态类型的可以随便加槽（本质上是个字典）。所以压根没什么二进制结构。
# 只能用dataclass做一些运行时的辅助检查之类的

STATUS_XXX = 1
STATUS_YYY = 2

FILE = 'shelve.db'

import shelve


@dataclass
class Message:
    id: int
    send_time : datetime
    email_title : str
    email_content :str
    status :int

    db = shelve.open('Message.db')

    def __str__(self):
        return f"Message {self.email_title} {self.status} at {self.send_time}"

    def __lt__(self, other):
        return self.send_time < other.send_time
    
    

def getAllMessage():
    return list(Message.db.values())



@dataclass
class Event:
    message_id: int
    detail :str
    event_time :datetime

    db = shelve.open('Event.db')

    def __str__(self):
        return f"Event at {self.event_time} said {self.detail} for {self.message}"

def getAllEvent():
    return list(Event.db.values())