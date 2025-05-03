from rq import Worker
from app.core.redis_conn import redis_conn, request_queue
import multiprocessing

multiprocessing.set_start_method('spawn', force=True)
listen = [request_queue]

if __name__ == "__main__":
    worker = Worker(listen, connection=redis_conn)
    worker.work()
