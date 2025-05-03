from pydantic import BaseModel

class Scrape(BaseModel):
    job_title: str
    location: str
    experience: str | None = None