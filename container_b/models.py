from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class InterpolNotice(Base):
    __tablename__ = 'interpol_notices'

    entity_id = Column(String, primary_key=True, index=True)
    forename = Column(String, nullable=True)
    name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    nationalities = Column(JSON, nullable=True)
    arrest_warrants = Column(JSON, nullable=True)
    fetch_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_updated = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'entity_id': self.entity_id,
            'forename': self.forename,
            'name': self.name,
            'date_of_birth': self.date_of_birth,
            'nationalities': self.nationalities,
            'arrest_warrants': self.arrest_warrants,
            'fetch_timestamp': self.fetch_timestamp.isoformat() if self.fetch_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_updated': self.is_updated
        }
