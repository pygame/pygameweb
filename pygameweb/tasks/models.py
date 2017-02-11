"""
"""
from math import sqrt
from pathlib import Path

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        Table, Text, inspect, BIGINT, PrimaryKeyConstraint,
                        CheckConstraint, text, TEXT, Index)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import count
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSON


from pygameweb.models import Base, metadata
from pygameweb.user.models import User
from pygameweb.config import Config
from pygameweb.thumb import image_thumb

from pygameweb.sanitize import sanitize_html


class Queue(Base):
    __tablename__ = 'queue'

    id = Column(BIGINT(), primary_key=True, nullable=False)
    queue_pkey = PrimaryKeyConstraint('id')
    enqueued_at = Column(TIMESTAMP(timezone=True),
                         server_default=text('now()'),
                         autoincrement=False,
                         nullable=False)
    enqueued_at = Column(TIMESTAMP(timezone=True),
                         server_default=text('now()'),
                         autoincrement=False,
                         nullable=False)
    dequeued_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    expected_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    schedule_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    q_name = Column(TEXT(),
                    CheckConstraint('length(q_name) > 0', name='queue_q_name_check'),
                    autoincrement=False,
                    nullable=False)

    data = Column(JSON(astext_type=Text()), autoincrement=False, nullable=False)

    __table_args__ = (Index('priority_idx', "schedule_at", "expected_at"), )
