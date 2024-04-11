'''
Debug Hint:
    > python -m pdb -m notification_app.startup
    > r
    > Ctrl-C
    > addOneMessage()
    > os._exit(0) # important, if use q, you will be stuck
                  # because this weird program cannot handle SIGINT
'''
# LOOP就是Scheduler的黑话版本。小彭老师有一个C++协程的课，推荐去看看。
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from vendor.mail.mailqq import senderSend
import data.models as mo

q = asyncio.Queue()
cancel = None
loop = asyncio.new_event_loop()

def recover():
    '''Recover from unexpected shutdown'''
    import data.models as mo
    db = mo.Message.db
    for k in db.keys():
        val: mo.Message = db[k]
        status = val.status
        if ((status=='busy') or(status=='scheduled')or (status=='fail')):
            val.status='idle'
            db[k] = val

def on_sigint(signum, frame):
    fCancel.set_result(object())


def onSendTimeout(m, ret):
    print(f'timeout during sending "{m}"')
    e = mo.newEvent(message=m, detail = f'timeout during sending "{m}", ret = {ret}')
    mo.saveEvent(e)
    m.status = 'fail'
    mo.saveMessage(m)

def onSendSuccess(m,ret):
    e = mo.newEvent(message=m, detail = f'successfully sent "{m}", ret = {ret}')
    mo.saveEvent(e)
    print(f'* successfully sent "{m}", ret = {ret}')
    if not ret:
        m.status = 'done'
    else:
        m.status = 'fail'
    mo.saveMessage(m)

async def sendMessage(m, p):
    '''发送的任务'''
    print(f'* trying to send "{m}"')
    t = loop.run_in_executor(p, senderSend, m.email_title, m.email_content)
    print(f'* running senderSend thread on "{m}"')
    try:
        ret = await asyncio.wait_for(t, timeout=5)
        onSendSuccess(m,ret)
    except asyncio.TimeoutError:
        onSendTimeout(m,ret)
    
def run_loop():
    
    print('in main')
    import signal
    loop.add_signal_handler(signal.SIGINT, on_sigint)
    loop.add_signal_handler(signal.SIGTERM, on_sigint)

    recover()

    loop.run_until_complete(mainCoro())

def run_loop_with_new_thread()->Thread:
    thread = Thread(target = run_loop)
    thread.start()
    return thread

async def wait_until(dt):
    '''这是个辅助用的awaitable'''
    # sleep until the specified datetime
    now = datetime.datetime.now()
    await asyncio.sleep((dt - now).total_seconds())

fCancel = asyncio.Future()

async def waitAndDispatchOneMessage(m:mo.Message):
    '''代表一个消息发送的长时任务，并且支持cancel'''
    async def task():
        await wait_until(m.send_time)
        sendMessage(m)
    await asyncio.wait([fCancel,task],return_when=asyncio.FIRST_COMPLETED)

async def mainCoro():
    '''负责不断取新消息的长时任务'''
    while True:
        if fCancel.done():
            return
        m: mo.Message = await q.get() # recv a new Message
        mo.Message.db[m.id] = m # save it  # TODO: 同步的存储操作改成异步，并且用协程包装一下。
        cur_loop = asyncio.get_event_loop() # 拿到loop并且塞一个发送任务上去。
        asyncio.run_coroutine_threadsafe(waitAndDispatchOneMessage(m), cur_loop)
