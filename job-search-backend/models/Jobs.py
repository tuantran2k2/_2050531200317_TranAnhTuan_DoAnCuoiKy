from sqlalchemy import Column, String, DateTime
from database._database_mysql import Base


class Job(Base):
    __tablename__ = "job"

    id_job = Column(String(20), primary_key=True)
    job_title = Column(String(255), nullable=False)
    link_post = Column(String(2083), nullable=False)
    location = Column(String(255))
    date_post = Column(DateTime)