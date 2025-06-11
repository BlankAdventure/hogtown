# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 20:56:41 2025

@author: BlankAdventure
"""

import datetime
from enum import Enum
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Integer, JSON
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

# declarative base class
class Base(DeclarativeBase):
    pass

class ORM_model(Base):
    __tablename__ = "events_json"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    data: Mapped[str] = mapped_column(JSON)

#'sqlite:///./json_events.db'
def session_factory(db_url: str = 'sqlite://') -> sessionmaker:
    """Factory function to create engine and session for dependency injection."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    #Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return sessionmaker(bind=engine, expire_on_commit=False)



class Route(str, Enum):
    AA = "A to A"
    AB = "A to B"

class Event_model(BaseModel):
    title: str
    date: datetime.date = Field(description="ISO format date", ge=datetime.date.today())
    time: datetime.time = Field(description="ISO format time")
    hosts: List[str]
    location: str
    ttc: str = Field(default='')
    cost: float = Field(default=10.00, ge=0.0)
    route: Route = Route.AA
    comments: str = Field(default='')
    rsvp: List[str] = Field(default=[])

    class Config:
        validate_assignment = True
        revalidate_instances = 'always'
        extra = 'forbid'

class EventRepository:
    """Repository to handle database operations."""
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def add_event(self, event: ORM_model) -> bool:
        try:
           with self.session_factory.begin() as sesh:
               sesh.add(event)
               return True
        except Exception as e:
           print(e)
           return False


    def get_all_events(self, skip: int = 0, limit: int = 100) -> List[ORM_model]:
        with self.session_factory.begin() as sesh:
            return sesh.query(ORM_model).offset(skip).limit(limit).all()

    def get_event_by_id(self, event_id: int) -> Optional[ORM_model]:
        with self.session_factory.begin() as sesh:
            return sesh.query(ORM_model).filter(ORM_model.id == event_id).first()

    def update_event(self, event: ORM_model) -> bool:
        try:
            with self.session_factory.begin() as sesh:
                sesh.merge(event)
                return True
        except Exception:
            return False

    def delete_event(self, event_id: int) -> bool:
        event = self.get_event_by_id(event_id)
        if event:
            try:
                with self.session_factory.begin() as sesh:
                    sesh.delete(event)
                    return True
            except Exception:
                return False
        return False

class EventService:
    """Service layer for business logic."""
    def __init__(self, repository: EventRepository):
        self.repository = repository

    def create_event(self, data: dict) -> Event_model:
        """Validate and create an Event_model from dictionary."""
        return Event_model(**data)

    def to_orm(self, data: dict) -> ORM_model:
        """Convert dictionary to ORM object."""
        event = self.create_event(data)
        return ORM_model(data=event.model_dump_json())

    def from_orm(self, event: ORM_model) -> Event_model:
        """Convert ORM object to Event_model."""
        return Event_model(**json.loads(event.data))

    def add_event(self, data: dict) -> bool:
        """Add a new event to the database."""
        orm_event = self.to_orm(data)
        return self.repository.add_event(orm_event)

    def get_all_events(self, skip: int = 0, limit: int = 100) -> List[tuple[Event_model, int]]:
        """Retrieve all events, converted to Event_model."""
        orm_events = self.repository.get_all_events(skip, limit)
        return [(self.from_orm(event), event.id) for event in orm_events]

    def modify_event(self, event_id: int, new_data: dict) -> bool:
        """Modify an existing event."""
        orm_event = self.repository.get_event_by_id(event_id)
        if not orm_event:
            return False
        orig_data = dict(self.from_orm(orm_event))
        merged = orig_data | new_data
        
        try:
            updated = self.create_event(merged)
        except Exception as e:
               print(e)
               return False

        orm_event.data = updated.model_dump_json()
        return self.repository.update_event(orm_event)
            
         
    def add_rsvp(self, event_id: int, name: str) -> bool:
        """Add new name to RSVP list."""
        orm_event = self.repository.get_event_by_id(event_id)
        if not orm_event:
            return False
        orig_event = self.from_orm(orm_event)
        orig_event.rsvp.append(name)
        orm_event.data = orig_event.model_dump_json()
        return self.repository.update_event(orm_event)

    def delete_event(self, event_id: int) -> bool:
        """Delete an event by ID."""
        return self.repository.delete_event(event_id)
    
    
# data = {
#     "title": "Test Event",
#     "date": date.today().isoformat(),
#     "time": time(14, 30).isoformat(),
#     "hosts": ["Alice", "Bob"],
#     "location": "Test City",
#     "ttc": "Bus",
#     "cost": 15.00,
#     "route": "A to A",
#     "comments": "Test comment",
#     "rsvp": ["Charlie"]
# }    

# #Sesh = session_factory('sqlite:///:memory:')    
# repo = EventRepository( session_factory() )
# service = EventService(repo)
# service.add_event(data)
# res = service.add_rsvp(1, "Alex")           