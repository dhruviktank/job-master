from redis import Redis
from rq import Queue
from app.core.config import settings

redis_conn = Redis(
    host='redis-17369.c16.us-east-1-3.ec2.redns.redis-cloud.com',
    port=17369,
    decode_responses=True,
    username="default",
    password="K7QZEul2GgrsxBr2koiZC4m5sR3ULGfG"
)

request_queue = Queue('request_queue', connection=redis_conn)
linkedin_mainQ = Queue('linkedin_main_scraper', connection=redis_conn)
linkedin_urlQ = Queue('linkedin_url_scraper', connection=redis_conn)
