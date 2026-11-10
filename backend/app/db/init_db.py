"""
FraudShield Database Initialization and Seeding Script.
Creates database schema and seeds initial administrative credentials and champion model version.
"""

import json
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.db.base import Base
from backend.app.db.session import SessionLocal, engine
from backend.app.models.model_version import ModelStatus, ModelVersion
from backend.app.models.user import User, UserRole

import time

logger = logging.getLogger("FraudShield.InitDB")


def init_db(max_retries: int = 5, retry_delay: float = 2.0) -> None:
    """Creates schema and seeds initial administrative user and model record with retry logic."""
    logger.info("Verifying database schema and initial tables...")
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            if attempt == max_retries:
                logger.error("Failed to connect to database after %d attempts: %s", max_retries, e)
                raise
            logger.warning("Database connection attempt %d/%d failed (%s). Retrying in %.1fs...", attempt, max_retries, e, retry_delay)
            time.sleep(retry_delay)

    with SessionLocal() as session:
        # 1. Seed Superuser
        user_stmt = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL.lower().strip())
        admin = session.execute(user_stmt).scalars().first()

        if not admin:
            logger.info("Creating initial administrator (%s)...", settings.FIRST_SUPERUSER_EMAIL)
            admin = User(
                email=settings.FIRST_SUPERUSER_EMAIL.lower().strip(),
                full_name=settings.FIRST_SUPERUSER_NAME,
                password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            session.add(admin)
            session.flush()
            logger.info("Initial administrator created successfully.")
        else:
            logger.info("Administrator user already exists.")

        # 2. Seed Champion Model Version
        meta_file = settings.ARTIFACTS_DIR / "metadata.json"
        meta = {}
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

        ver_stmt = select(ModelVersion).where(
            ModelVersion.version == settings.CHAMPION_MODEL_VERSION
        )
        model_ver = session.execute(ver_stmt).scalars().first()

        if not model_ver:
            logger.info("Registering Champion model version (%s)...", settings.CHAMPION_MODEL_VERSION)
            model_ver = ModelVersion(
                version=settings.CHAMPION_MODEL_VERSION,
                model_name=meta.get("model_name", "XGBoost"),
                artifact_path=str(settings.ARTIFACTS_DIR / "model.joblib"),
                metrics=meta.get("test_metrics", {}),
                status=ModelStatus.ACTIVE.value,
                approved_by=admin.id,
            )
            session.add(model_ver)
            session.flush()
            logger.info("Champion model version registered.")

        session.commit()
        logger.info("Database initialization completed successfully.")


if __name__ == "__main__":
    init_db()
