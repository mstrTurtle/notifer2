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

q:asyncio.Queue = None
fCancel: asyncio.Future = None
cancel = None
loop = asyncio.new_event_loop()

def _recover():
    '''Recover from unexpected shutdown'''
    import data.models as mo
    db = mo.Message.db
    for k in db.keys():
        val: mo.Message = db[k]
        status = val.status
        if ((status=='busy') or(status=='scheduled')or (status=='fail')):
            val.status='idle'
            db[k] = val

sig_flag = False

def _on_sigint(signum, frame):
    print('on sigint')
    global sig_flag
    if not sig_flag:
        fCancel.set_result(object())
        sig_flag = True


def _onSendTimeout(m, ret):
    print(f'timeout during sending "{m}"')
    e = mo.newEvent(message=m, detail = f'timeout during sending "{m}", ret = {ret}')
    mo.saveEvent(e)
    m.status = 'fail'
    mo.saveMessage(m)

def _onSendSuccess(m,ret):
    e = mo.newEvent(message=m, detail = f'successfully sent "{m}", ret = {ret}')
    mo.saveEvent(e)
    print(f'* successfully sent "{m}", ret = {ret}')
    if not ret:
        m.status = 'done'
    else:
        m.status = 'fail'
    mo.saveMessage(m)

async def _sendMessage(m, p):
    '''发送的任务'''
    print(f'* trying to send "{m}"')
    t = loop.run_in_executor(p, senderSend, m.email_title, m.email_content)
    print(f'* running senderSend thread on "{m}"')
    try:
        ret = await asyncio.wait_for(t, timeout=5)
        _onSendSuccess(m,ret)
    except asyncio.TimeoutError:
        _onSendTimeout(m,ret)
    
def run_loop():
    
    print('in main')
    import signal
    # loop.add_signal_handler(signal.SIGINT, on_sigint)
    # loop.add_signal_handler(signal.SIGTERM, on_sigint)

    
    signal.signal(signal.SIGINT, _on_sigint)
    signal.signal(signal.SIGTERM, _on_sigint)

    _recover()

    # while True:
    try:
        # 如果你用这个run_until_complete，你得额外包裹一层cancel, supress, run之类的东西才能正确处理KeyInterrupt之类的。
        # https://stackoverflow.com/a/58532304/2073595 Python3.7+之后建议直接使用asyncio.run().
        # loop.run_until_complete(mainCoro()) 
        asyncio.set_event_loop(loop)
        asyncio.run(_mainCoro()) # 这是run_until_complete加强易用版本。在其外面包了一层supress，再次运行等的东西
    except KeyboardInterrupt:
        print("on key intr")
        _on_sigint(None,None)
        # import os
        # os._exit(42)

def run_loop_with_new_thread()->Thread:
    thread = Thread(target = run_loop)
    thread.start()
    return thread

async def wait_until(dt):
    '''这是个辅助用的awaitable'''
    # sleep until the specified datetime
    now = datetime.datetime.now()
    if dt <= now:
        return
    await asyncio.sleep((dt - now).total_seconds())


async def _waitAndDispatchOneMessage(m:mo.Message):
    '''代表一个消息发送的长时任务，并且支持cancel'''
    async def dispatchCoro():
        try:
            await wait_until(m.send_time)
            _sendMessage(m)
        except asyncio.CancelledError:
            print(f'Message {m.id}\'s sending is gracefully closed')
        task = dispatchCoro()
        await asyncio.wait([fCancel,task],return_when=asyncio.FIRST_COMPLETED)
   

async def _mainCoro():
    '''负责不断取新消息的长时任务'''
    global q, fCancel
    q = asyncio.Queue()
    fCancel = asyncio.Future()
    while True:
        task = asyncio.create_task(q.get())
        print('before wait')
        finished, unfinished = await asyncio.wait([fCancel,task],return_when=asyncio.FIRST_COMPLETED) # recv a new Message
        print('after wait')
        if fCancel.done():
            return
        m: mo.Message = finished[0].result()
        mo.Message.db[str(m.id)] = m # save it  # TODO: 同步的存储操作改成异步，并且用协程包装一下。
        cur_loop = asyncio.get_event_loop() # 拿到loop并且塞一个发送任务上去。
        asyncio.run_coroutine_threadsafe(_waitAndDispatchOneMessage(m), cur_loop)
