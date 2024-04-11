from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

import logging
logger = logging.getLogger(__name__)

# https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design
# 按照这玩意儿的表格设计。/xs(四个操作), /xs/{id}(没POST之外三个操作), /xs/{id}/ys（四个操作）都定义上去。
# 像个矩阵一样。有些东西用不到暂时先不定义了。


import data.models as m

@app.get("/messages")
def messages_list():
    ms = m.getAllMessage()
    return  {'messages': ms}


@app.get("/events")
def events_list():
    es = m.getAllEvent()
    return  {'events': es}

@app.delete("/messages/{id}")
def cancel_message(id:int):
    val = m.Message.db[id]
    val.status = 'canceled'
    m.Message.db[id] = val
    return RedirectResponse(url='/redirected')

@app.post("/messages")
def message_list(mm: m.Message):
    # TODO: id应当根据最大的生成
    m.Message.db[mm.id] = mm
    emit('message updated in list')
    # TODO: 通知消息模块进行通信