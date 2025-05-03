from redis import Redis
from rq import Queue
from app.core.config import settings

redis_conn = Redis(host=settings.redis_host, port=settings.redis_port)

request_queue = Queue('request_queue', connection=redis_conn)
linkedin_mainQ = Queue('linkedin_main_scraper', connection=redis_conn)
linkedin_urlQ = Queue('linkedin_url_scraper', connection=redis_conn)
