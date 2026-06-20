from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(String(20), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))
    priority = Column(String(20))
    status = Column(String(30), default='Open')
    attachment_url = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime)

class TicketHistory(Base):
    __tablename__ = "ticket_history"
    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(20), ForeignKey('tickets.ticket_id'))
    old_status = Column(String(30))
    new_status = Column(String(30))
    changed_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    comments = Column(Text)
    changed_at = Column(DateTime, server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    session_id = Column(UUID(as_uuid=True))
    user_message = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    article_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    category = Column(String(100))
    content = Column(Text, nullable=False)
    keywords = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime, server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    action = Column(String(255))
    entity_type = Column(String(50))
    entity_id = Column(String(100))
    details = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_name = Column(String(255))
    generated_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    report_data = Column(JSON)
    generated_at = Column(DateTime, server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    otp = Column(String(10))
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
