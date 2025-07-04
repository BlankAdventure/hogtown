# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 21:02:56 2025

@author: BlankAdventure
"""

import pytest
from unittest.mock import Mock
from datetime import date, time
from ..hogtown.model import Event_model, EventService, EventRepository, session_factory

@pytest.fixture
def in_memory_db():
    """Create an in-memory database for testing."""
    return session_factory('sqlite://')

#@pytest.fixture
def event_data():
    """Sample event data for testing."""
    return {
        "title": "Test Event",
        "date": date.today().isoformat(),
        "time": time(14, 30).isoformat(),
        "hosts": ["Alice", "Bob"],
        "location": "Test City",
        "ttc": "Bus",
        "cost": 15.00,
        "route": "A to A",
        "comments": "Test comment",
        "rsvp": ["Charlie"]
    }

def test_create_event_valid():
    """Test creating a valid Event_model."""
    repo = Mock(spec=EventRepository)
    service = EventService(repo)
    event = service.create_event(event_data())
    assert isinstance(event, Event_model)
    assert event.title == "Test Event"
    assert len(event.hosts) == 2

def test_create_event_invalid_data():
    """Test creating an event with invalid data."""
    repo = Mock(spec=EventRepository)
    service = EventService(repo)
    invalid_data = {"title": "Test", "date": "invalid-date", "time": "14:30", "hosts": [], "location": "City"}
    with pytest.raises(ValueError):
        service.create_event(invalid_data)


def test_add_event_success(in_memory_db): 
    """Test adding an event to the database."""
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    result = service.add_event(event_data())
    assert result is True
    events = service.get_all_events()
    assert len(events) == 1
    assert events[0][0].title == "Test Event"
    assert events[0][1] == 1


def test_modify_event_success(in_memory_db):
    """Test modifying an existing event."""
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    service.add_event(event_data())
    new_data = {"title": "Updated Event"}
    result = service.modify_event(1, new_data)
    assert result is True
    events = service.get_all_events()
    assert events[0][0].title == "Updated Event"

def test_modify_event_fail(in_memory_db):
    """Test modifying an existing event."""
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    service.add_event(event_data())
    new_data = {"tit": "Updated Event"}
    result = service.modify_event(1, new_data)
    assert result is False

def test_delete_event_success(in_memory_db):
    """Test deleting an event."""
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    service.add_event(event_data())
    result = service.delete_event(1)
    assert result is True
    events = service.get_all_events()
    assert len(events) == 0


def test_modify_event_not_found(in_memory_db):
    """Test modifying a non-existent event."""
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    result = service.modify_event(999, {"title": "Non-existent"})
    assert result is False

def test_add_rsvp(in_memory_db):
    repo = EventRepository(in_memory_db)
    service = EventService(repo)
    service.add_event(event_data())
    result = service.add_rsvp(1, "Alex")
    assert result is True
    events = service.get_all_events()
    assert events[0][0].rsvp[1] == "Alex"
    
# def test_modify_event_not_found(in_memory_db):
#     """Test modifying a non-existent event."""
#     repo = EventRepository(in_memory_db())
#     service = EventService(repo)
#     result = service.modify_event(999, {"title": "Non-existent"})
#     assert result is False

        
        
#test_add_event_success(in_memory_db, event_data)
#repo = EventRepository(in_memory_db())
#service = EventService(repo)
#service.add_event(event_data())       
        