from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog


def log_event(db: Session, action: str, entity_type: str, entity_id: str | None = None, user_id: int | None = None, ip: str | None = None, user_agent: str | None = None):
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, user_id=user_id, ip_address=ip, user_agent=user_agent))
