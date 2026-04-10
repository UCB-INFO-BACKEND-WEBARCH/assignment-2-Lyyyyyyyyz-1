import os
from redis import Redis
from rq import Worker, Queue
from dotenv import load_dotenv

load_dotenv()

print("WORKER STARTING") # check 有没有开始 

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url)

if __name__ == "__main__": 
    print("CONNECTING TO REDIS:", redis_url)
    queue = Queue("default", connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    print("WORKER RUNNING...")
    worker.work()