"""
FraudShield Audit Log Repository.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog
from backend.app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: Session):
        super().__init__(AuditLog, session)

    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details or {},
        )
        return self.create(log_entry)

    def list_logs(self, limit: int = 50, offset: int = 0) -> List[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())
