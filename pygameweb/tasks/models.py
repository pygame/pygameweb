""" A queue for tasks and jobs, and messages, and such like.
"""
from sqlalchemy import (Column, Text, BIGINT, PrimaryKeyConstraint,
                        CheckConstraint, text, TEXT, Index)
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSON


from pygameweb.models import Base


class Queue(Base):
    __tablename__ = 'queue'

    id = Column(BIGINT(), primary_key=True, nullable=False)
    queue_pkey = PrimaryKeyConstraint('id')
    enqueued_at = Column(TIMESTAMP(timezone=True),
                         server_default=text('now()'),
                         autoincrement=False,
                         nullable=False)
    dequeued_at = Column(TIMESTAMP(timezone=True),
                         autoincrement=False,
                         nullable=True)
    expected_at = Column(TIMESTAMP(timezone=True),
                         autoincrement=False,
                         nullable=True)
    schedule_at = Column(TIMESTAMP(timezone=True),
                         autoincrement=False,
                         nullable=True)
    q_name = Column(TEXT(),
                    CheckConstraint('length(q_name) > 0',
                                    name='queue_q_name_check'),
                    autoincrement=False,
                    nullable=False)
    data = Column(JSON(astext_type=Text()),
                  autoincrement=False,
                  nullable=False)
    __table_args__ = (Index('priority_idx', "schedule_at", "expected_at"), )
