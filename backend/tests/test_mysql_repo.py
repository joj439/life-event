import pytest
from sqlalchemy import create_engine, text
from app.config import settings
from app.db.connection import check_db_connection, verify_db_connection
from app.repositories.factory import get_repository, reset_repository_instances
from app.repositories.in_memory_repo import InMemoryRepository
from app.repositories.mysql_repo import MySQLRepository
from app.schemas.models import (
    LifeEvent,
    ContextAnswers,
    DocumentStatus,
    ApplicationStatus
)

# SQLite DDL mirroring the exact schema of MySQL `lifeevent_db`
SCHEMA_DDL = """
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE life_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(150) NOT NULL,
    description VARCHAR(500),
    portal_url VARCHAR(500)
);

CREATE TABLE event_services (
    event_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (event_id, service_id),
    FOREIGN KEY (event_id) REFERENCES life_events(event_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name VARCHAR(150) NOT NULL
);

CREATE TABLE service_documents (
    service_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    PRIMARY KEY (service_id, document_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE TABLE user_documents (
    user_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Needed',
    PRIMARY KEY (user_id, document_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE TABLE applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Not Started',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE application_status_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

CREATE TRIGGER application_status_update
AFTER UPDATE ON applications
FOR EACH ROW
WHEN OLD.status <> NEW.status
BEGIN
    INSERT INTO application_status_history (application_id, old_status, new_status)
    VALUES (NEW.application_id, OLD.status, NEW.status);
END;

CREATE VIEW user_application_summary AS
SELECT
    u.user_id,
    u.name AS user_name,
    le.event_type,
    s.service_name,
    a.status,
    a.created_at
FROM users u
JOIN life_events le ON u.user_id = le.user_id
JOIN event_services es ON le.event_id = es.event_id
JOIN services s ON es.service_id = s.service_id
JOIN applications a ON a.user_id = u.user_id AND a.service_id = s.service_id;
"""

INITIAL_DATA_SQL = """
INSERT INTO users (name, email) VALUES ('Demo User', 'demo@lifeevent.com');

INSERT INTO services (service_name, description, portal_url) VALUES
('Address Update', 'Update address details after relocation', 'https://www.uidai.gov.in/'),
('PDS / Ration Update', 'Update or transfer PDS related information', 'https://nfsa.gov.in/'),
('Vehicle Update', 'Update vehicle related records after relocation', 'https://parivahan.gov.in/'),
('Government Benefits Review', 'Review government benefits after relocation', 'https://www.india.gov.in/'),
('Financial Cyber Fraud Reporting', 'Report financial cyber fraud through the official portal', 'https://cybercrime.gov.in/'),
('Marriage Registration', 'Access marriage registration related services', 'https://www.india.gov.in/'),
('Aadhaar Demographic Update', 'Access Aadhaar demographic update services', 'https://myaadhaar.uidai.gov.in/'),
('Death Registration & Certificate', 'Access death registration and certificate services', 'https://crsorgi.gov.in/'),
('Pension & Survivor Review', 'Review pension and survivor related services', 'https://www.india.gov.in/');

INSERT INTO documents (document_name) VALUES
('Identity Proof'),
('Address Proof'),
('Vehicle Registration'),
('PDS / Ration Card');

INSERT INTO service_documents (service_id, document_id) VALUES
(1, 1), (1, 2),
(2, 1), (2, 2), (2, 4),
(3, 1), (3, 2), (3, 3),
(4, 1), (4, 2);

INSERT INTO user_documents (user_id, document_id, status) VALUES
(1, 1, 'Available'),
(1, 2, 'Available'),
(1, 3, 'Needed'),
(1, 4, 'Needed');

INSERT INTO applications (user_id, service_id, status) VALUES
(1, 1, 'Completed'),
(1, 2, 'Under Review'),
(1, 3, 'Action Required'),
(1, 4, 'Not Started');

INSERT INTO life_events (user_id, event_type, description) VALUES
(1, 'Relocation', 'Moved from Mumbai to Pune');

INSERT INTO event_services (event_id, service_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4);
"""


@pytest.fixture
def mock_db_engine():
    """Create an in-memory SQL database with the exact schema and data of lifeevent_db."""
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    with engine.connect() as conn:
        conn.connection.dbapi_connection.executescript(SCHEMA_DDL)
        conn.connection.dbapi_connection.executescript(INITIAL_DATA_SQL)
    return engine


@pytest.fixture
def test_repo(mock_db_engine):
    """Instantiate MySQLRepository pointing to the test engine."""
    return MySQLRepository(engine=mock_db_engine)


# =============================================================================
# 1. Connection & Fail-Fast Tests
# =============================================================================

def test_check_db_connection_returns_bool():
    """check_db_connection should execute without throwing uncaught exceptions."""
    result = check_db_connection()
    assert isinstance(result, bool)


def test_verify_db_connection_fail_fast_on_invalid_credentials(monkeypatch):
    """When USE_MYSQL=True and credentials fail, a clear descriptive RuntimeError must be raised."""
    monkeypatch.setattr(settings, "MYSQL_PASSWORD", "definitely_invalid_password_xyz_123")
    monkeypatch.setattr(settings, "USE_MYSQL", True)
    reset_repository_instances()

    with pytest.raises(RuntimeError) as exc_info:
        verify_db_connection()
    error_msg = str(exc_info.value)
    assert "lifeevent_db" in error_msg
    assert "MYSQL_PASSWORD" in error_msg


def test_factory_defaults_to_in_memory():
    """When USE_MYSQL=False, get_repository() must return InMemoryRepository."""
    reset_repository_instances()
    orig = settings.USE_MYSQL
    try:
        settings.USE_MYSQL = False
        repo = get_repository()
        assert isinstance(repo, InMemoryRepository)
    finally:
        settings.USE_MYSQL = orig


# =============================================================================
# 2. Services & Catalog Tests
# =============================================================================

def test_mysql_repo_get_all_services(test_repo):
    """Verify services catalog retrieval and document requirements mapping."""
    services = test_repo.get_all_services()
    assert len(services) >= 9
    service_map = {s.id: s for s in services}
    assert "address_update" in service_map
    assert "pds_update" in service_map
    assert "vehicle_update" in service_map
    assert "benefits_review" in service_map

    # Address Update requires identity_proof and address_proof
    addr = service_map["address_update"]
    assert "identity_proof" in addr.required_document_ids
    assert "address_proof" in addr.required_document_ids


def test_mysql_repo_get_service_by_id(test_repo):
    """Verify single service lookup by string code or numeric id."""
    s1 = test_repo.get_service_by_id("address_update")
    assert s1 is not None
    assert s1.name == "Address Update"

    s2 = test_repo.get_service_by_id("1")
    assert s2 is not None
    assert s2.name == "Address Update"

    missing = test_repo.get_service_by_id("non_existent_service")
    assert missing is None


# =============================================================================
# 3. Documents & User Document Tracking Tests
# =============================================================================

def test_mysql_repo_document_types(test_repo):
    """Verify document types catalog retrieval."""
    docs = test_repo.get_all_document_types()
    assert len(docs) >= 4
    doc_map = {d.id: d for d in docs}
    assert "identity_proof" in doc_map
    assert "address_proof" in doc_map

    single = test_repo.get_document_type("identity_proof")
    assert single is not None
    assert single.name == "Identity Proof"


def test_mysql_repo_user_documents(test_repo):
    """Verify user document status retrieval from user_documents table."""
    user_docs = test_repo.get_user_documents("usr_demo_citizen")
    assert "identity_proof" in user_docs
    assert "address_proof" in user_docs
    assert "vehicle_reg" in user_docs

    # Initial demo state: Identity & Address proof are Available, Vehicle Reg is Missing
    assert user_docs["identity_proof"].status == DocumentStatus.AVAILABLE
    assert user_docs["address_proof"].status == DocumentStatus.AVAILABLE
    assert user_docs["vehicle_reg"].status == DocumentStatus.MISSING


def test_mysql_repo_toggle_document_status(test_repo):
    """Verify toggling document availability in user_documents."""
    # Initially Missing
    doc_before = test_repo.get_user_documents("usr_demo_citizen")["vehicle_reg"]
    assert doc_before.status == DocumentStatus.MISSING

    # Toggle to Available
    updated = test_repo.toggle_user_document_status("usr_demo_citizen", "vehicle_reg", DocumentStatus.AVAILABLE)
    assert updated is not None
    assert updated.status == DocumentStatus.AVAILABLE

    # Confirm in persistence
    doc_after = test_repo.get_user_documents("usr_demo_citizen")["vehicle_reg"]
    assert doc_after.status == DocumentStatus.AVAILABLE

    # Toggle back without explicit status -> should toggle to Missing
    toggled_again = test_repo.toggle_user_document_status("usr_demo_citizen", "vehicle_reg")
    assert toggled_again.status == DocumentStatus.MISSING


# =============================================================================
# 4. Applications, Status Update & Trigger History Tests
# =============================================================================

def test_mysql_repo_applications(test_repo):
    """Verify applications retrieval and status mapping."""
    apps = test_repo.get_user_applications("usr_demo_citizen")
    assert len(apps) >= 4

    app_map = {a.service_id: a for a in apps}
    assert "address_update" in app_map
    assert app_map["address_update"].status == ApplicationStatus.COMPLETED
    assert app_map["pds_update"].status == ApplicationStatus.UNDER_REVIEW


def test_mysql_repo_get_application_by_id(test_repo):
    """Verify application lookup by seed code and numeric ID."""
    app_addr = test_repo.get_application_by_id("app_addr_01")
    assert app_addr is not None
    assert app_addr.status == ApplicationStatus.COMPLETED

    app_numeric = test_repo.get_application_by_id("1")
    assert app_numeric is not None
    assert app_numeric.status == ApplicationStatus.COMPLETED


def test_mysql_repo_trigger_generated_history(test_repo):
    """
    Verify application status update fires the database TRIGGER `application_status_update`
    and records an audit entry in `application_status_history`.
    """
    # Initially no history for app 2 (PDS Update: currently 'Under Review')
    history_before = test_repo.get_application_status_history("app_pds_02")
    initial_count = len(history_before)

    # Update status to 'Action Required'
    success = test_repo.update_application_status("app_pds_02", "Action Required")
    assert success is True

    # Verify history recorded by trigger
    history_after = test_repo.get_application_status_history("app_pds_02")
    assert len(history_after) == initial_count + 1
    latest_entry = history_after[-1]
    assert latest_entry["old_status"] == "Under Review"
    assert latest_entry["new_status"] == "Action Required"

    # Verify application reflects new status
    app = test_repo.get_application_by_id("app_pds_02")
    assert app.status == ApplicationStatus.ACTION_REQUIRED


# =============================================================================
# 5. Database VIEW & Stored Procedure / Journey Tests
# =============================================================================

def test_mysql_repo_view_user_application_summary(test_repo):
    """Verify querying the database VIEW `user_application_summary`."""
    summary_rows = test_repo.get_user_application_summary("usr_demo_citizen")
    assert len(summary_rows) >= 1
    first_row = summary_rows[0]
    assert first_row["user_name"] == "Demo User"
    assert first_row["event_type"] == "Relocation"
    assert "service_name" in first_row
    assert "status" in first_row


# =============================================================================
# 6. Life Events, Context & Reset Demo State
# =============================================================================

def test_mysql_repo_life_events_and_event_services(test_repo):
    """Verify life event persistence and event_services association."""
    event = LifeEvent(
        id="evt_test_relocation",
        raw_input="Moved from Pune to Delhi",
        event_type="relocation",
        origin="Pune",
        destination="Delhi"
    )
    saved = test_repo.save_life_event(event)
    assert saved.id == "evt_test_relocation"

    retrieved = test_repo.get_life_event("evt_test_relocation")
    assert retrieved is not None
    assert retrieved.event_type == "relocation"

    # Update context
    ctx = ContextAnswers(permanent=True, owns_vehicle=False, receives_pds=True)
    updated = test_repo.update_life_event_context("evt_test_relocation", ctx)
    assert updated.context.owns_vehicle is False
    assert updated.context.receives_pds is True


def test_mysql_repo_reset_demo_state(test_repo):
    """Verify reset_demo_state restores user documents and application statuses."""
    # Modify states
    test_repo.toggle_user_document_status("usr_demo_citizen", "vehicle_reg", DocumentStatus.AVAILABLE)
    test_repo.update_application_status("app_addr_01", "Action Required")

    # Reset
    test_repo.reset_demo_state()

    # Confirm restored
    docs = test_repo.get_user_documents("usr_demo_citizen")
    assert docs["vehicle_reg"].status == DocumentStatus.MISSING
    assert docs["identity_proof"].status == DocumentStatus.AVAILABLE

    app1 = test_repo.get_application_by_id("app_addr_01")
    assert app1.status == ApplicationStatus.COMPLETED
