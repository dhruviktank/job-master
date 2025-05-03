from app.models.request.scraper import Scrape
from app.services.scraper.site.linkedin import LinkedInScraper
from app.services.scraper.site.indeed import IndeedScraper
from app.services.scraper.site.naukri import NaukriScraper
from app.services.scraper.site.glassdoor import GlassdoorScraper
from app.core.redis_conn import linkedin_mainQ
from app.core.redis_conn import request_queue, redis_conn
from rq import get_current_job
from memory_profiler import profile
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class ScraperTask:
    def __init__(self, scrape_request: Scrape):
        self.scrape_request = scrape_request

    def get_jobs(self):
        # job = get_current_job()
        # job = request_queue.enqueue(scraper_task.get_jobs)
        logger.info('Entering in Request Queue')
        # linkedin_scraper = LinkedInScraper(self.scrape_request)
        # jobs = linkedin_scraper.execute()
        indeed_scraper = NaukriScraper(self.scrape_request)
        indeedJobs = request_queue.enqueue(indeed_scraper.execute)
        linkedin_scraper = LinkedInScraper(self.scrape_request)
        linkedinJobs = request_queue.enqueue(linkedin_scraper.execute)
        glassdoor_scraper = GlassdoorScraper(self.scrape_request)
        glassdoorJobs = request_queue.enqueue(glassdoor_scraper.execute)
        # sub_job_ids = []
        # a = 0
        # for job_data in jobs:
        #     if (job_data['url']):
        #         a = a+1
        #         sub_job = linkedin_mainQ.enqueue(indeed_scraper.get_url_data, job_data['url'], str(a))
        #         sub_job_ids.append(sub_job.id)

        # # Store sub-job ids into main job metadata
        # job.meta['sub_jobs'] = sub_job_ids
        # job.save_meta()  # VERY IMPORTANT to persist meta
        return [indeedJobs.id, linkedinJobs.id, glassdoorJobs.id]
        # return [glassdoorJobs.id]
