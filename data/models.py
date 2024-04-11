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
    
def saveMessage(m:Message):
    Message.db[m.id] = m

def getAllMessage():
    return list(Message.db.values())

cntDb=shelve.open('cnt.db')
if 'Message' not in cntDb:
    cntDb['Message'] = 0
if 'Event' not in cntDb:
    cntDb['Event'] = 0

def getCnt(key:str):
    v = cntDb[key]
    cntDb[key] = v+1
    return v


@dataclass
class Event:
    id: int
    message_id: int
    detail :str
    event_time :datetime

    db = shelve.open('Event.db')

    def __str__(self):
        return f"Event at {self.event_time} said {self.detail} for {self.message}"

def getAllEvent():
    return list(Event.db.values())

def saveEvent(e:Event):
    Message.db[e.id] = e

def newEvent(m:Message, detail:str)->Event:
    return Event(id=getCnt('Event'),message_id=m.id,detail=detail,event_time=datetime.now())
    raise NotImplementedError()