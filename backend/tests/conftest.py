"""
Pytest Fixtures for FraudShield Test Suite.
Configures isolated test database, seeded users, and HTTPX test client.
"""

import os
from pathlib import Path
import sys
from typing import AsyncGenerator, Dict, Generator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set test environment and local matplotlib cache
os.environ["MPLCONFIGDIR"] = str(Path(__file__).resolve().parent.parent.parent / ".matplotlib_cache")

from backend.app.core.config import settings
settings.ENVIRONMENT = "testing"

from backend.app.core.security import create_access_token, get_password_hash
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.ml.loader import model_manager
from backend.app.models.model_version import ModelStatus, ModelVersion
from backend.app.models.user import User, UserRole

# Isolated SQLite test database
TEST_DB_PATH = Path("test_fraudshield.db")
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def setup_test_database():
    """Initializes tables and seeds initial test users before each test."""
    if not model_manager.is_loaded:
        model_manager.load_artifacts()

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestSessionLocal() as session:
        admin = User(
            id="test-admin-uuid-1",
            email="admin@fraudshield.io",
            full_name="System Admin",
            password_hash=get_password_hash("AdminPassword123!"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        investigator = User(
            id="test-investigator-uuid-2",
            email="investigator@fraudshield.io",
            full_name="Jane Investigator",
            password_hash=get_password_hash("Investigator123!"),
            role=UserRole.INVESTIGATOR.value,
            is_active=True,
        )
        test_user = User(
            id="test-regular-user-uuid-3",
            email="user@fraudshield.io",
            full_name="John Customer",
            password_hash=get_password_hash("UserPassword123!"),
            role=UserRole.USER.value,
            is_active=True,
        )
        model_ver = ModelVersion(
            id="test-model-ver-1",
            version="v1.0.0",
            model_name="XGBoost",
            artifact_path="ml/artifacts/model.joblib",
            metrics={"pr_auc": 1.0, "roc_auc": 1.0, "f1": 1.0},
            status=ModelStatus.ACTIVE.value,
            approved_by=admin.id,
        )
        session.add_all([admin, investigator, test_user, model_ver])
        session.commit()

    yield


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous HTTPX test client overriding database session dependency."""
    def override_get_db() -> Generator[Session, None, None]:
        db = TestSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers() -> Dict[str, str]:
    token = create_access_token(subject="test-admin-uuid-1", role=UserRole.ADMIN.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def investigator_headers() -> Dict[str, str]:
    token = create_access_token(subject="test-investigator-uuid-2", role=UserRole.INVESTIGATOR.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers() -> Dict[str, str]:
    token = create_access_token(subject="test-regular-user-uuid-3", role=UserRole.USER.value)
    return {"Authorization": f"Bearer {token}"}
