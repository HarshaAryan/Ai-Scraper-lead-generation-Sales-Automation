"""Database models and operations using SQLite"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings
import json

Base = declarative_base()

class LeadModel(Base):
    """Lead storage model"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Business Info
    company_name = Column(String(255), nullable=False)
    website = Column(String(512), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    
    # Metadata
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    source_url = Column(String(512), nullable=True)
    website_status = Column(String(50), default="unknown")  # active, missing, 404, unknown
    
    # Categorization
    query_type = Column(String(100), nullable=True)  # local_business, lead_gen, etc.
    industry = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Enrichment
    notes = Column(Text, nullable=True)
    raw_data = Column(Text, nullable=True)  # JSON dump of all scraped data
    
    # Timestamps
    found_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_qualified = Column(Boolean, default=False)
    contacted = Column(Boolean, default=False)

class JobModel(Base):
    """Job/Query tracking"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, nullable=False)
    
    query = Column(Text, nullable=False)
    query_type = Column(String(100), nullable=True)
    
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Results
    leads_found = Column(Integer, default=0)
    urls_scraped = Column(Integer, default=0)
    
    # Metadata
    plan = Column(Text, nullable=True)  # JSON array of steps
    messages = Column(Text, nullable=True)  # JSON array of agent messages
    error = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Database:
    """Database manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def save_lead(self, lead_data: dict):
        """Save a lead to the database"""
        session = self.get_session()
        try:
            lead = LeadModel(
                company_name=lead_data.get("company_name", "Unknown"),
                website=lead_data.get("website"),
                phone=lead_data.get("phone"),
                email=lead_data.get("email"),
                address=lead_data.get("address"),
                rating=lead_data.get("rating"),
                reviews=lead_data.get("reviews"),
                source_url=lead_data.get("source_url"),
                website_status=lead_data.get("website_status", "unknown"),
                query_type=lead_data.get("query_type"),
                industry=lead_data.get("industry"),
                location=lead_data.get("location"),
                notes=lead_data.get("notes"),
                raw_data=json.dumps(lead_data)
            )
            session.add(lead)
            session.commit()
            return lead.id
        finally:
            session.close()
    
    def save_job(self, job_data: dict):
        """Save a job to the database"""
        session = self.get_session()
        try:
            job = JobModel(
                job_id=job_data.get("job_id"),
                query=job_data.get("query"),
                query_type=job_data.get("query_type"),
                status=job_data.get("status", "pending"),
                plan=json.dumps(job_data.get("plan", [])),
                messages=json.dumps(job_data.get("messages", []))
            )
            session.add(job)
            session.commit()
            return job.id
        finally:
            session.close()
    
    def get_all_leads(self, limit: int = 100):
        """Get all leads"""
        session = self.get_session()
        try:
            return session.query(LeadModel).order_by(LeadModel.found_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_leads_by_query_type(self, query_type: str):
        """Get leads filtered by query type"""
        session = self.get_session()
        try:
            return session.query(LeadModel).filter(LeadModel.query_type == query_type).all()
        finally:
            session.close()

# Global database instance
db = Database()
