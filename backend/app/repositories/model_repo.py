"""
FraudShield Model Version Governance Repository.
"""

from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.models.model_version import ModelStatus, ModelVersion
from backend.app.repositories.base import BaseRepository


class ModelRepository(BaseRepository[ModelVersion]):
    def __init__(self, session: Session):
        super().__init__(ModelVersion, session)

    def get_active_model(self) -> Optional[ModelVersion]:
        stmt = (
            select(ModelVersion)
            .where(ModelVersion.status == ModelStatus.ACTIVE.value)
            .order_by(ModelVersion.created_at.desc())
        )
        return self.session.execute(stmt).scalars().first()

    def get_by_version(self, version: str) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).where(ModelVersion.version == version)
        return self.session.execute(stmt).scalars().first()

    def list_versions(self) -> List[ModelVersion]:
        stmt = select(ModelVersion).order_by(ModelVersion.created_at.desc())
        return list(self.session.execute(stmt).scalars().all())

    def promote_version(self, version_id: str, approver_id: Optional[str]) -> Optional[ModelVersion]:
        # 1. Deprecate active models
        self.session.execute(
            update(ModelVersion)
            .where(ModelVersion.status == ModelStatus.ACTIVE.value)
            .values(status=ModelStatus.DEPRECATED.value)
        )
        # 2. Promote target
        target = self.get_by_id(version_id)
        if target:
            target.status = ModelStatus.ACTIVE.value
            target.approved_by = approver_id
            self.session.flush()
            self.session.refresh(target)
        return target
