'''
Debug Hint:
    > python -m pdb -m notification_app.startup
    > r
    > Ctrl-C
    > addOneMessage()
    > os._exit(0) # important, if use q, you will be stuck
                  # because this weird program cannot handle SIGINT
'''
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_project.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
import django
django.setup()

from .models import Message, Event
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
from .mailqq import senderSend
import datetime
import asyncio
import heapq

from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from django.db.models import Q
tasks = set()
heap = []

async def trySend(m, p):
    print(f'* trying to send "{m}"')
    t = loop.run_in_executor(p, senderSend, m.email_title, m.email_content)
    print(f'* running senderSend thread on "{m}"')
    try:
        ret = await asyncio.wait_for(t, timeout=5)
    except asyncio.TimeoutError:
        print(f'timeout during sending "{m}"')
        m.status = 'fail'
        m.save()
        return
    Event.objects.create(message=m, detail = f'successfully sent "{m}", ret = {ret}')
    print(f'* successfully sent "{m}", ret = {ret}')
    if not ret:
        m.status = 'done'
    else:
        m.status = 'fail'
    m.save()

def recover():
    '''Recover from unexpected shutdown'''
    for m in Message.objects.filter(Q(status='busy') | Q(status='scheduled')| Q(status='fail')):
        m.status='idle'
        m.save()

time_tasks = []

async def run():
    '''create timer heap and start sending loop'''
    print('- in run')
    for m in Message.objects.filter(status='idle'):
        heapq.heappush(heap, m)
    while True:
        # detect cancel or not
        if cancel:
            print('Start cancel and gracefully shutdown')
            for t in tasks:
                await t
            return
        print(f'- detecting heap: heap = {heap}')
        # sleep for the next job
        if heap:
            gap = (heap[0].send_time - timezone.now()).total_seconds()
            print(f'-- in schedule sleep of gap, gap = {gap}')
            if gap <= 0:
                print(f'--- gap < 0 so send immediately')
                m = heapq.heappop(heap)
                m.refresh_from_db()
                if m.status == 'canceled':
                    continue
                m.status = 'busy'
                m.save()
                tasks.add(asyncio.create_task(trySend(m, p)))
                continue
            else:
                async def time_activate():
                    print(f'--- scheduled time_activate task in {gap} secs')
                    heap[0].status = 'scheduled'
                    heap[0].save()
                    await asyncio.sleep(gap)
                    sem.release()
                tasks.add(asyncio.create_task(time_activate()))
        print(f'-- before sem cond')
        await sem.acquire()
        print(f'-- after sem cond')
async def addMessageCoroImpl(m):
    '''For loop schedule. Dont call directly'''
    m.save()
    heapq.heappush(heap, m)
    # no matter heap empty or not, should notify
    # in case detect not empty here but empty after 0.0001 second.
    print('before notify')
    sem.release()
    print('after notify')

def submitMessage(m, timeout = None):
    '''sync submit message'''
    future = asyncio.run_coroutine_threadsafe(addMessageCoroImpl(m), loop)
    return future.result(timeout)

def submitMessageAsync(m):
    '''async submit message'''
    future = asyncio.run_coroutine_threadsafe(addMessageCoroImpl(m), loop)
    return future

def addOneMessage():
    '''this is for test. we submit a xxx yyy message'''
    submitMessage(Message.objects.create(send_time=timezone.now(),
        email_title = 'xxxx',
        email_content = 'xxxxyyyyy',
        status = 'idle'))


cond = asyncio.Condition()
sem = asyncio.Semaphore(0)
#loop = asyncio.get_event_loop()
loop = asyncio.new_event_loop()

p = ThreadPoolExecutor(4) # Create a ThreadPool with 4 processes

# variable for gracefully shutdown
cancel = False

def on_sigint(signum, frame):
    print('in on_sigint')
    global cancel
    async def do_cancel():
        cancel = True
        sem.release()
    loop.call_soon_threadsafe(do_cancel)
from threading import Thread

def startup_spawn():
    print('in main')
    #import signal
    #signal.signal(signal.SIGINT, on_sigint)
    #signal.signal(signal.SIGTERM, on_sigint)
    recover()

    def run_thread():
        print('in run_thread')
        # loop.add_signal_handler(signal.SIGINT, on_sigint)
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
        
    thread = Thread(target = run_thread)
    thread.start()
if __name__=='__main__':
    startup_spawn()
