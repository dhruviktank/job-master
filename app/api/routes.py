from fastapi import APIRouter
from app.core.redis_conn import request_queue, redis_conn
from app.services.healthcheck_task import health_check_job
from app.workers.tasks import ScraperTask, Scrape
from app.services.scraper.site.linkedin import LinkedInScraper
from rq import job
from rq.job import Job
import asyncio
import time
import json

router = APIRouter()

@router.post("/scrape")
async def scrape_jobs(request: Scrape):
    start = time.time()
    scraper_task = ScraperTask(request)
    sub_job_ids = scraper_task.get_jobs()
    
    # Wait for main job to finish
    # while not (job.is_finished or job.is_failed):
    #     await asyncio.sleep(0.5)
    #     job.refresh()

    # Check if there are subjobs
    all_sub_sub_job_ids = []
    # sub_job_ids = job.meta.get('sub_jobs', [])
    result = []
    for sub_job_id in sub_job_ids:
        sub_job = Job.fetch(sub_job_id, connection=redis_conn)
        while not (sub_job.is_finished or sub_job.is_failed):
            await asyncio.sleep(0.5)
            sub_job.refresh()

        if sub_job.meta and 'sub_jobs' in sub_job.meta:
            all_sub_sub_job_ids.extend(sub_job.meta['sub_jobs'])

    final_results = []
    for sub_sub_job_id in all_sub_sub_job_ids:
        sub_sub_job = Job.fetch(sub_sub_job_id, connection=redis_conn)
        while not (sub_sub_job.is_finished or sub_sub_job.is_failed):
            await asyncio.sleep(0.5)
            sub_sub_job.refresh()

        # Once finished, collect result
        if sub_sub_job.result:
            final_results.append(sub_sub_job.result)

    end = time.time()
    print(f"Scraping finished in {end - start:.2f} seconds")

    return {
        "status": "success",
        "total_time_seconds": round(end - start, 2),
        "final_results": final_results
    }

@router.get("/polling/{job_id}")
async def poll_job(job_id):
    job_1 = job.Job.fetch(job_id, redis_conn)
    return {
        "response": "success",
        "job_id": job_id,
        "job_status": [job_1.is_canceled, job_1.is_finished],
        "result": job_1.result
    }

@router.get("/scrape/status/{job_id}")
async def get_scrape_job_status(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)

    if job.is_finished:
        sub_jobs_status = []
        sub_job_ids = job.meta.get('sub_jobs', [])

        for sub_job_id in sub_job_ids:
            sub_job = Job.fetch(sub_job_id, connection=redis_conn)
            sub_jobs_status.append({
                "job_id": sub_job_id,
                "status": sub_job.get_status(),
                "result": sub_job.result if sub_job.is_finished else None
            })

        return {
            "status": "finished",
            "sub_jobs": sub_jobs_status,
            "result": job.result
        }
    elif job.is_failed:
        return {"status": "failed"}
    else:
        return {"status": "in_progress"}
    

@router.post("/healthcheck")
async def run_healthcheck():
    job = request_queue.enqueue(health_check_job)
    return {"job_id": job.id}