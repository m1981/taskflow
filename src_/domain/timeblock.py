from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from .task import ZoneType, EnergyLevel

"""
Time block management for task scheduling.

Domain Context:
- Represents schedulable time periods
- Defines work zones with specific characteristics
- Manages existing calendar events
- Handles buffer time requirements

Business Rules:
- Zones have specific energy levels and constraints
- Minimum duration requirements per zone type
- Buffer time must be maintained between blocks
- Fixed events cannot be modified

Architecture:
- TimeBlock is base class for all time periods
- TimeBlockZone adds zone-specific constraints
- Event represents calendar entries
- Immutable design for time block properties

System Constraints:
- Time blocks cannot overlap
- Zones must have minimum duration
- Events must fit within block boundaries
"""

class TimeBlockType(Enum):
    FIXED = "fixed"
    MANAGED = "managed"
    ZONE = "zone"

class Event:
    def __init__(self, id: str, start: datetime, end: datetime, 
                 title: str, type: TimeBlockType, buffer_required: int = 0):
        self.id = id
        self.start = start
        self.end = end
        self.title = title
        self.type = type
        self.buffer_required = buffer_required  # New field for buffer requirements

@dataclass
class TimeBlock:
    start: datetime
    end: datetime
    type: TimeBlockType
    events: List[Event] = field(default_factory=list)

    def is_available(self, start: datetime, duration: int) -> bool:
        if start < self.start or start + timedelta(minutes=duration) > self.end:
            return False
        return len(self.get_conflicts(start, duration)) == 0

    def get_conflicts(self, start: datetime, duration: int) -> List[Event]:
        end = start + timedelta(minutes=duration)
        return [
            event for event in self.events
            if (start < event.end and end > event.start)
        ]

@dataclass
class TimeBlockZone:
    start: datetime
    end: datetime
    zone_type: ZoneType
    energy_level: EnergyLevel
    min_duration: int  # in minutes
    buffer_required: int  # in minutes
    type: TimeBlockType = TimeBlockType.ZONE
    events: List[Event] = field(default_factory=list)

    def is_available(self, start: datetime, duration: int) -> bool:
        # Check if duration meets minimum requirement
        if duration < self.min_duration:
            return False
            
        # Check time bounds and conflicts
        if start < self.start or start + timedelta(minutes=duration) > self.end:
            return False
        return len(self.get_conflicts(start, duration)) == 0

    def get_conflicts(self, start: datetime, duration: int) -> List[Event]:
        # Basic time conflicts
        end = start + timedelta(minutes=duration)
        conflicts = [
            event for event in self.events
            if (start < event.end and end > event.start)
        ]
        
        # Check for buffer violations
        if self.buffer_required > 0:
            buffer_start = start - timedelta(minutes=self.buffer_required)
            buffer_end = start + timedelta(minutes=duration + self.buffer_required)
            
            buffer_conflicts = [
                event for event in self.events
                if (buffer_start < event.end and buffer_end > event.start)
                and event not in conflicts
            ]
            
            conflicts.extend(buffer_conflicts)
            
        return conflicts

class AdminZoneType(Enum):
    EMAIL = "email"
    PLANNING = "planning"
    REVIEW = "review"

@dataclass(frozen=True)
class AdminZoneConfig:
    zone_type: AdminZoneType
    preferred_time: str  # e.g., "morning", "afternoon"
    max_duration: int  # minutes
    required_buffer: int  # minutes
    energy_threshold: EnergyLevel

class AdminTimeBlockZone(TimeBlockZone):
    def __init__(
        self,
        start: datetime,
        end: datetime,
        admin_config: AdminZoneConfig,
        events: List[Event] = None
    ):
        super().__init__(
            start=start,
            end=end,
            zone_type=ZoneType.ADMIN,
            energy_level=EnergyLevel.MEDIUM,
            min_duration=15,
            buffer_required=admin_config.required_buffer,
            events=events or []
        )
        self.admin_config = admin_config

    def validate_task_placement(self, task: Task, start_time: datetime) -> bool:
        """Validate if admin task can be placed in this zone"""
        if not super().validate_task_placement(task, start_time):
            return False
            
        # Check admin-specific constraints
        if task.duration > self.admin_config.max_duration:
            return False
            
        if self.current_energy_level < self.admin_config.energy_threshold:
            return False
            
        return True
