from . import startup as s
import asyncio

async def addMessageCoro(m):
    '''For loop schedule. Dont call directly'''
    s.q.put(m)

def submitMessage(m, timeout = None):
    '''sync submit message'''
    future = asyncio.run_coroutine_threadsafe(addMessageCoro(m), s.loop)
    return future.result(timeout)

def submitMessageAsync(m):
    '''async submit message'''
    future = asyncio.run_coroutine_threadsafe(addMessageCoro(m), s.loop)
    return future