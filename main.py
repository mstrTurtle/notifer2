from api.views import app
from message_loop.startup import loop, run_loop
import uvicorn
import threading

def run_server():
    uvicorn.run(app=app,port=8088)

t = threading.Thread(target=run_server)
t.start()
run_loop()
print("run end")
t.join()

# run_loop()