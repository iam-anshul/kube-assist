from sqlalchemy import (
    Column, TIMESTAMP, ForeignKey, ForeignKeyConstraint,
    func, LargeBinary, JSON, Integer, String, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Projects(Base):
    __tablename__ = "user_projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=func.now())

    chat_ids = relationship('ChatIDs', back_populates="projects", cascade="all, delete-orphan", passive_deletes=True)
    message_history = relationship('MessageHistory', back_populates='projects', cascade='all, delete-orphan', passive_deletes=True)
    conversation = relationship('Conversation', back_populates='projects', cascade='all, delete-orphan', passive_deletes=True)
    kube_config = relationship('KubeConfig', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)
    cloud_creds = relationship("CloudCreds", back_populates='project', cascade='all, delete-orphan', passive_deletes=True)


class ChatIDs(Base):
    __tablename__ = "chatIDs"

    user_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("user_projects.project_id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=func.now())

    chats = relationship('MessageHistory', back_populates='parent_chat', cascade='all, delete-orphan', passive_deletes=True)
    conversations = relationship('Conversation', back_populates='parent', cascade='all, delete-orphan', passive_deletes=True)
    projects = relationship('Projects', back_populates='chat_ids')
    task = relationship('Tasks', back_populates='chatid', passive_deletes=True, cascade="all, delete-orphan")


class MessageHistory(Base):
    __tablename__ = "message_history"
    
    chat_data_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chatIDs.chat_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("user_projects.project_id", ondelete="CASCADE"), nullable=False)
    data = Column(LargeBinary, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    parent_chat = relationship('ChatIDs', back_populates='chats')
    projects = relationship('Projects', back_populates='message_history')


class Conversation(Base):
    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint('project_id', 'chat_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    conversation_count = Column(Integer)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chatIDs.chat_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("user_projects.project_id", ondelete="CASCADE"), nullable=False)
    user_conversation = Column(JSON)

    parent = relationship('ChatIDs', back_populates='conversations')
    projects = relationship('Projects', back_populates='conversation')


class Tasks(Base):
    __tablename__ = "tasks"

    user_id = Column(UUID(as_uuid=True), nullable=False)
    task_id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chatIDs.chat_id", ondelete="CASCADE"), nullable=False)
    task_status = Column(String(20), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    chatid = relationship('ChatIDs', back_populates='task')

class KubeConfig(Base):
    __tablename__ = 'kubeconfigs'

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False, unique=False)
    project_id = Column(UUID, ForeignKey('user_projects.project_id', ondelete='CASCADE'), nullable=False)
    config = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    context_name = Column(LargeBinary, nullable=False, unique=True)
    kube_config_path = Column(LargeBinary, nullable=False, unique=True)

    project = relationship('Projects', back_populates='kube_config', passive_deletes=True)

class CloudCreds(Base):
    __tablename__ = 'cloud_creds'

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False, unique=False)
    project_id = Column(UUID, ForeignKey('user_projects.project_id', ondelete='CASCADE'), nullable=False)
    key = Column(LargeBinary, nullable=False)
    value = Column(LargeBinary, nullable=False)
    region = Column(LargeBinary, nullable=False)
    cluster_name = Column(LargeBinary, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    project = relationship('Projects', back_populates='cloud_creds', passive_deletes=True) 
