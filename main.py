from api.views import app
from message_loop.startup import loop, run_loop
import uvicorn
import threading

t = threading.Thread(target=run_loop)
uvicorn.run(app=app,port=8088)
t.start()
t.join()