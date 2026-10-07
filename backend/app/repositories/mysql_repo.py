import copy
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import text, Engine
from app.db.connection import get_engine
from app.repositories.base import BaseRepository
from app.schemas.models import (
    Service,
    DocumentType,
    UserDocument,
    Application,
    ApplicationStatus,
    DocumentStatus,
    LifeEvent,
    ContextAnswers
)
from app.data.seed_data import (
    SEED_SERVICES,
    SEED_DOCUMENT_TYPES,
    SEED_USER_DOCUMENTS,
    SEED_APPLICATIONS,
    DEMO_USER_ID
)

logger = logging.getLogger(__name__)

# Two-way ID mappings between string codes and MySQL integer IDs
SERVICE_STR_TO_INT = {
    "address_update": 1,
    "pds_update": 2,
    "vehicle_update": 3,
    "benefits_review": 4,
    "cyber_fraud_complaint": 5,
    "financial_fraud_reporting": 5,
    "marriage_registration": 6,
    "aadhaar_demographic_update": 7,
    "death_registration": 8,
    "pension_survivor_review": 9
}

SERVICE_INT_TO_STR = {
    1: "address_update",
    2: "pds_update",
    3: "vehicle_update",
    4: "benefits_review",
    5: "cyber_fraud_complaint",
    6: "marriage_registration",
    7: "aadhaar_demographic_update",
    8: "death_registration",
    9: "pension_survivor_review"
}

DOC_STR_TO_INT = {
    "identity_proof": 1,
    "address_proof": 2,
    "vehicle_reg": 3,
    "pds_ration_card": 4,
    "txn_details": 5,
    "marriage_proof": 6,
    "hospital_death_report": 7
}

DOC_INT_TO_STR = {
    1: "identity_proof",
    2: "address_proof",
    3: "vehicle_reg",
    4: "pds_ration_card",
    5: "txn_details",
    6: "marriage_proof",
    7: "hospital_death_report"
}

APP_STR_TO_SERVICE_INT = {
    "app_addr_01": 1,
    "app_pds_02": 2,
    "app_veh_03": 3,
    "app_ben_04": 4,
    "app_fraud_05": 5,
    "app_marriage_06": 6,
    "app_death_07": 7
}

MYSQL_STATUS_TO_APP_STATUS = {
    "Not Started": ApplicationStatus.NOT_STARTED,
    "Under Review": ApplicationStatus.UNDER_REVIEW,
    "Action Required": ApplicationStatus.ACTION_REQUIRED,
    "Completed": ApplicationStatus.COMPLETED
}

APP_STATUS_TO_MYSQL_STATUS = {
    ApplicationStatus.NOT_STARTED: "Not Started",
    ApplicationStatus.READY: "Not Started",
    ApplicationStatus.SUBMITTED: "Under Review",
    ApplicationStatus.UNDER_REVIEW: "Under Review",
    ApplicationStatus.ACTION_REQUIRED: "Action Required",
    ApplicationStatus.COMPLETED: "Completed"
}


class MySQLRepository(BaseRepository):
    """
    MySQL-backed repository communicating with lifeevent_db.
    Preserves existing Pydantic response contracts, leverages existing database
    features (VIEW user_application_summary, STORED PROCEDURE get_user_journey,
    TRIGGER application_status_update), and uses parameterized SQL queries.
    """

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()
        self._life_events_cache: Dict[str, LifeEvent] = {}

    def _resolve_user_id(self, user_id: str) -> int:
        if user_id == DEMO_USER_ID:
            return 1
        try:
            return int(user_id)
        except ValueError:
            return 1

    # =========================================================================
    # Services Catalog
    # =========================================================================

    def get_all_services(self) -> List[Service]:
        """
        Retrieve all services from MySQL `services` table, joined with required
        documents from `service_documents`, preserving Pydantic schema.
        """
        services_map: Dict[int, Service] = {}
        with self.engine.connect() as conn:
            # 1. Fetch all services
            svc_rows = conn.execute(
                text("SELECT service_id, service_name, description, portal_url FROM services ORDER BY service_id ASC")
            ).fetchall()

            # 2. Fetch all service-document associations
            doc_rows = conn.execute(
                text("SELECT service_id, document_id FROM service_documents ORDER BY service_id, document_id")
            ).fetchall()

        svc_doc_map: Dict[int, List[str]] = {}
        for row in doc_rows:
            sid, did = row[0], row[1]
            doc_code = DOC_INT_TO_STR.get(did, f"doc_{did}")
            svc_doc_map.setdefault(sid, []).append(doc_code)

        for row in svc_rows:
            sid = row[0]
            name = row[1]
            desc = row[2] or ""
            portal_url = row[3] or ""

            str_code = SERVICE_INT_TO_STR.get(sid, f"service_{sid}")
            req_docs = svc_doc_map.get(sid, [])

            seed_template = SEED_SERVICES.get(str_code)
            if seed_template:
                service = seed_template.model_copy(
                    update={
                        "id": str_code,
                        "name": name,
                        "description": desc or seed_template.description,
                        "portal_url": portal_url or seed_template.portal_url,
                        "required_document_ids": req_docs or seed_template.required_document_ids
                    }
                )
            else:
                service = Service(
                    id=str_code,
                    name=name,
                    category="Government Service",
                    description=desc,
                    why_relevant="Official government service.",
                    required_document_ids=req_docs,
                    basic_steps=[
                        "Fill out online request form.",
                        "Upload required documents.",
                        "Track status."
                    ],
                    applicable_life_events=["relocation"],
                    portal_name=name,
                    portal_url=portal_url,
                    is_mock_portal=False,
                    estimated_processing_days=7
                )
            services_map[sid] = service

        return list(services_map.values())

    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        """
        Retrieve a specific service by string ID (e.g. 'address_update') or integer ID.
        """
        sid = SERVICE_STR_TO_INT.get(service_id)
        if sid is None and service_id.isdigit():
            sid = int(service_id)

        with self.engine.connect() as conn:
            if sid is not None:
                row = conn.execute(
                    text("SELECT service_id, service_name, description, portal_url FROM services WHERE service_id = :sid"),
                    {"sid": sid}
                ).fetchone()
            else:
                row = conn.execute(
                    text("SELECT service_id, service_name, description, portal_url FROM services WHERE service_name LIKE :name LIMIT 1"),
                    {"name": f"%{service_id}%"}
                ).fetchone()

            if not row:
                return None

            actual_sid = row[0]
            name = row[1]
            desc = row[2] or ""
            portal_url = row[3] or ""

            doc_rows = conn.execute(
                text("SELECT document_id FROM service_documents WHERE service_id = :sid"),
                {"sid": actual_sid}
            ).fetchall()
            req_docs = [DOC_INT_TO_STR.get(r[0], f"doc_{r[0]}") for r in doc_rows]

        str_code = SERVICE_INT_TO_STR.get(actual_sid, service_id)
        seed_template = SEED_SERVICES.get(str_code)
        if seed_template:
            return seed_template.model_copy(
                update={
                    "id": str_code,
                    "name": name,
                    "description": desc or seed_template.description,
                    "portal_url": portal_url or seed_template.portal_url,
                    "required_document_ids": req_docs or seed_template.required_document_ids
                }
            )

        return Service(
            id=str_code,
            name=name,
            category="Government Service",
            description=desc,
            why_relevant="Official government service.",
            required_document_ids=req_docs,
            basic_steps=[
                "Fill out online request form.",
                "Upload required documents.",
                "Track status."
            ],
            applicable_life_events=["relocation"],
            portal_name=name,
            portal_url=portal_url,
            is_mock_portal=False,
            estimated_processing_days=7
        )

    # =========================================================================
    # Document Catalog & User Document Tracking
    # =========================================================================

    def get_all_document_types(self) -> List[DocumentType]:
        """
        Retrieve all document types from MySQL `documents` table.
        """
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT document_id, document_name FROM documents ORDER BY document_id ASC")
            ).fetchall()

        results: List[DocumentType] = []
        for row in rows:
            did = row[0]
            name = row[1]
            code = DOC_INT_TO_STR.get(did, f"doc_{did}")
            template = SEED_DOCUMENT_TYPES.get(code)
            if template:
                results.append(
                    template.model_copy(
                        update={
                            "id": code,
                            "code": code,
                            "name": name
                        }
                    )
                )
            else:
                results.append(
                    DocumentType(
                        id=code,
                        code=code,
                        name=name,
                        description=f"Official {name} verification document.",
                        accepted_examples=[name],
                        is_information_item=False
                    )
                )
        return results

    def get_document_type(self, doc_type_id: str) -> Optional[DocumentType]:
        """
        Retrieve a single document type specification.
        """
        did = DOC_STR_TO_INT.get(doc_type_id)
        if did is None and doc_type_id.isdigit():
            did = int(doc_type_id)

        with self.engine.connect() as conn:
            if did is not None:
                row = conn.execute(
                    text("SELECT document_id, document_name FROM documents WHERE document_id = :did"),
                    {"did": did}
                ).fetchone()
            else:
                row = conn.execute(
                    text("SELECT document_id, document_name FROM documents WHERE document_name LIKE :name LIMIT 1"),
                    {"name": f"%{doc_type_id}%"}
                ).fetchone()

        if not row:
            return None

        actual_did = row[0]
        name = row[1]
        code = DOC_INT_TO_STR.get(actual_did, doc_type_id)
        template = SEED_DOCUMENT_TYPES.get(code)
        if template:
            return template.model_copy(
                update={"id": code, "code": code, "name": name}
            )

        return DocumentType(
            id=code,
            code=code,
            name=name,
            description=f"Official {name} verification document.",
            accepted_examples=[name],
            is_information_item=False
        )

    def get_user_documents(self, user_id: str) -> Dict[str, UserDocument]:
        """
        Retrieve all document tracking records for a given user from MySQL `user_documents`.
        Initializes missing document types as MISSING/Needed to match repository contract.
        """
        uid = self._resolve_user_id(user_id)

        with self.engine.connect() as conn:
            # 1. Fetch all known documents
            all_docs = conn.execute(
                text("SELECT document_id, document_name FROM documents ORDER BY document_id ASC")
            ).fetchall()

            # 2. Fetch user's recorded status
            udoc_rows = conn.execute(
                text("SELECT document_id, status FROM user_documents WHERE user_id = :uid"),
                {"uid": uid}
            ).fetchall()

        user_status_map = {row[0]: row[1] for row in udoc_rows}

        results: Dict[str, UserDocument] = {}
        for row in all_docs:
            did = row[0]
            name = row[1]
            code = DOC_INT_TO_STR.get(did, f"doc_{did}")
            raw_status = user_status_map.get(did, "Needed")
            status = DocumentStatus.AVAILABLE if raw_status == "Available" else DocumentStatus.MISSING

            template = SEED_DOCUMENT_TYPES.get(code)
            is_info = template.is_information_item if template else False

            results[code] = UserDocument(
                id=f"udoc_{user_id}_{code}",
                user_id=user_id,
                document_type_id=code,
                document_name=name,
                status=status,
                is_information_item=is_info
            )

        # Include any remaining seed document types (e.g. information items like txn_details)
        for code, template in SEED_DOCUMENT_TYPES.items():
            if code not in results:
                results[code] = UserDocument(
                    id=f"udoc_{user_id}_{code}",
                    user_id=user_id,
                    document_type_id=code,
                    document_name=template.name,
                    status=DocumentStatus.MISSING,
                    is_information_item=template.is_information_item
                )

        return results

    def toggle_user_document_status(
        self, user_id: str, document_type_id: str, status: Optional[DocumentStatus] = None
    ) -> Optional[UserDocument]:
        """
        Toggle or set a user's document status in MySQL `user_documents`.
        """
        uid = self._resolve_user_id(user_id)
        did = DOC_STR_TO_INT.get(document_type_id)
        if did is None and document_type_id.isdigit():
            did = int(document_type_id)

        with self.engine.begin() as conn:
            # Check document existence
            if did is not None:
                doc_row = conn.execute(
                    text("SELECT document_id, document_name FROM documents WHERE document_id = :did"),
                    {"did": did}
                ).fetchone()
            else:
                doc_row = conn.execute(
                    text("SELECT document_id, document_name FROM documents WHERE document_name LIKE :name LIMIT 1"),
                    {"name": f"%{document_type_id}%"}
                ).fetchone()

            if not doc_row:
                # If document is a seed-only information item (e.g. txn_details)
                template = SEED_DOCUMENT_TYPES.get(document_type_id)
                if not template:
                    return None
                # Return updated in-memory UserDocument representation
                target_status = status if status is not None else DocumentStatus.AVAILABLE
                return UserDocument(
                    id=f"udoc_{user_id}_{document_type_id}",
                    user_id=user_id,
                    document_type_id=document_type_id,
                    document_name=template.name,
                    status=target_status,
                    is_information_item=template.is_information_item,
                    updated_at=datetime.now(timezone.utc).isoformat()
                )

            actual_did = doc_row[0]
            doc_name = doc_row[1]

            # Current status in user_documents
            current = conn.execute(
                text("SELECT status FROM user_documents WHERE user_id = :uid AND document_id = :did"),
                {"uid": uid, "did": actual_did}
            ).fetchone()

            if status is not None:
                new_db_status = "Available" if status == DocumentStatus.AVAILABLE else "Needed"
            else:
                if current and current[0] == "Available":
                    new_db_status = "Needed"
                else:
                    new_db_status = "Available"

            if self.engine.dialect.name == "sqlite":
                conn.execute(
                    text("""
                        INSERT INTO user_documents (user_id, document_id, status)
                        VALUES (:uid, :did, :st)
                        ON CONFLICT(user_id, document_id) DO UPDATE SET status = :st
                    """),
                    {"uid": uid, "did": actual_did, "st": new_db_status}
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO user_documents (user_id, document_id, status)
                        VALUES (:uid, :did, :st)
                        ON DUPLICATE KEY UPDATE status = :st
                    """),
                    {"uid": uid, "did": actual_did, "st": new_db_status}
                )

        final_status = DocumentStatus.AVAILABLE if new_db_status == "Available" else DocumentStatus.MISSING
        code = DOC_INT_TO_STR.get(actual_did, document_type_id)
        template = SEED_DOCUMENT_TYPES.get(code)
        is_info = template.is_information_item if template else False

        return UserDocument(
            id=f"udoc_{user_id}_{code}",
            user_id=user_id,
            document_type_id=code,
            document_name=doc_name,
            status=final_status,
            is_information_item=is_info,
            updated_at=datetime.now(timezone.utc).isoformat()
        )

    # =========================================================================
    # Applications & Database Features (VIEW, TRIGGER, STORED PROCEDURE)
    # =========================================================================

    def get_user_applications(self, user_id: str) -> List[Application]:
        """
        Retrieve all applications for the user, reading from MySQL `applications`
        and enriching with services and steps metadata.
        """
        uid = self._resolve_user_id(user_id)

        with self.engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT a.application_id, a.user_id, a.service_id, s.service_name, a.status, a.created_at
                    FROM applications a
                    JOIN services s ON a.service_id = s.service_id
                    WHERE a.user_id = :uid
                    ORDER BY a.application_id ASC
                """),
                {"uid": uid}
            ).fetchall()

        applications: List[Application] = []
        for row in rows:
            aid = row[0]
            sid = row[2]
            sname = row[3]
            db_status = row[4]
            created_at = row[5]

            status_enum = MYSQL_STATUS_TO_APP_STATUS.get(db_status, ApplicationStatus.NOT_STARTED)
            svc_str_code = SERVICE_INT_TO_STR.get(sid, f"service_{sid}")

            # Match with seed application for full timeline steps and metadata
            matched_app: Optional[Application] = None
            for app_key, seed_app in SEED_APPLICATIONS.items():
                if seed_app.service_id == svc_str_code:
                    matched_app = seed_app
                    break

            if matched_app:
                # Clone template and synchronize live status from MySQL
                app_copy = copy.deepcopy(matched_app)
                app_copy.status = status_enum
                app_copy.user_id = user_id
                app_copy.service_name = sname

                # Adjust step completions based on status
                if status_enum == ApplicationStatus.COMPLETED:
                    for step in app_copy.steps:
                        step.is_completed = True
                elif status_enum == ApplicationStatus.NOT_STARTED:
                    for step in app_copy.steps:
                        step.is_completed = False
                applications.append(app_copy)
            else:
                applied_date = str(created_at.date()) if created_at and hasattr(created_at, "date") else None
                applications.append(
                    Application(
                        id=f"app_{aid}",
                        user_id=user_id,
                        service_id=svc_str_code,
                        service_name=sname,
                        category="Government Services",
                        status=status_enum,
                        tracking_number=f"MH-2026-APP-{aid:04d}",
                        applied_date=applied_date,
                        remarks=f"Application status: {db_status}",
                        steps=[]
                    )
                )

        return applications

    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        """
        Retrieve a single application by tracking identifier or integer id.
        """
        target_sid = APP_STR_TO_SERVICE_INT.get(app_id)
        target_aid = None
        if target_sid is None:
            if app_id.isdigit():
                target_aid = int(app_id)
            elif app_id.startswith("app_") and app_id[4:].isdigit():
                target_aid = int(app_id[4:])

        with self.engine.connect() as conn:
            if target_sid is not None:
                row = conn.execute(
                    text("""
                        SELECT a.application_id, a.user_id, a.service_id, s.service_name, a.status, a.created_at
                        FROM applications a
                        JOIN services s ON a.service_id = s.service_id
                        WHERE a.service_id = :sid
                        ORDER BY a.application_id ASC LIMIT 1
                    """),
                    {"sid": target_sid}
                ).fetchone()
            elif target_aid is not None:
                row = conn.execute(
                    text("""
                        SELECT a.application_id, a.user_id, a.service_id, s.service_name, a.status, a.created_at
                        FROM applications a
                        JOIN services s ON a.service_id = s.service_id
                        WHERE a.application_id = :aid
                        LIMIT 1
                    """),
                    {"aid": target_aid}
                ).fetchone()
            else:
                return None

        if not row:
            return None

        aid = row[0]
        sid = row[2]
        sname = row[3]
        db_status = row[4]
        created_at = row[5]

        status_enum = MYSQL_STATUS_TO_APP_STATUS.get(db_status, ApplicationStatus.NOT_STARTED)
        svc_str_code = SERVICE_INT_TO_STR.get(sid, f"service_{sid}")

        matched_app: Optional[Application] = None
        if app_id in SEED_APPLICATIONS:
            matched_app = SEED_APPLICATIONS[app_id]
        else:
            for seed_app in SEED_APPLICATIONS.values():
                if seed_app.service_id == svc_str_code:
                    matched_app = seed_app
                    break

        if matched_app:
            app_copy = copy.deepcopy(matched_app)
            app_copy.status = status_enum
            app_copy.service_name = sname
            if status_enum == ApplicationStatus.COMPLETED:
                for step in app_copy.steps:
                    step.is_completed = True
            elif status_enum == ApplicationStatus.NOT_STARTED:
                for step in app_copy.steps:
                    step.is_completed = False
            return app_copy

        applied_date = str(created_at.date()) if created_at and hasattr(created_at, "date") else None
        return Application(
            id=app_id,
            user_id=DEMO_USER_ID,
            service_id=svc_str_code,
            service_name=sname,
            category="Government Services",
            status=status_enum,
            tracking_number=f"MH-2026-APP-{aid:04d}",
            applied_date=applied_date,
            remarks=f"Application status: {db_status}",
            steps=[]
        )

    def update_application_status(self, app_id: str, new_status: str) -> bool:
        """
        Updates the status of an application in MySQL `applications`.
        The existing MySQL TRIGGER `application_status_update` will automatically
        fire and record the transition into `application_status_history`.
        """
        target_sid = APP_STR_TO_SERVICE_INT.get(app_id)
        target_aid = None
        if target_sid is None:
            if app_id.isdigit():
                target_aid = int(app_id)
            elif app_id.startswith("app_") and app_id[4:].isdigit():
                target_aid = int(app_id[4:])

        # Normalize status to MySQL ENUM
        mysql_status = new_status
        for k, v in MYSQL_STATUS_TO_APP_STATUS.items():
            if new_status.lower() == v.value.lower() or new_status.lower() == k.lower():
                mysql_status = k
                break

        with self.engine.begin() as conn:
            if target_sid is not None:
                result = conn.execute(
                    text("UPDATE applications SET status = :st WHERE service_id = :sid"),
                    {"st": mysql_status, "sid": target_sid}
                )
            elif target_aid is not None:
                result = conn.execute(
                    text("UPDATE applications SET status = :st WHERE application_id = :aid"),
                    {"st": mysql_status, "aid": target_aid}
                )
            else:
                return False

            return result.rowcount > 0

    def get_application_status_history(self, app_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve audit history recorded by the `application_status_update` trigger.
        """
        target_sid = APP_STR_TO_SERVICE_INT.get(app_id)
        target_aid = None
        if target_sid is None:
            if app_id.isdigit():
                target_aid = int(app_id)
            elif app_id.startswith("app_") and app_id[4:].isdigit():
                target_aid = int(app_id[4:])

        with self.engine.connect() as conn:
            if target_sid is not None:
                app_row = conn.execute(
                    text("SELECT application_id FROM applications WHERE service_id = :sid"),
                    {"sid": target_sid}
                ).fetchone()
                if not app_row:
                    return []
                target_aid = app_row[0]

            if target_aid is None:
                return []

            rows = conn.execute(
                text("""
                    SELECT history_id, application_id, old_status, new_status, changed_at
                    FROM application_status_history
                    WHERE application_id = :aid
                    ORDER BY changed_at ASC, history_id ASC
                """),
                {"aid": target_aid}
            ).fetchall()

            return [
                {
                    "history_id": r[0],
                    "application_id": r[1],
                    "old_status": r[2],
                    "new_status": r[3],
                    "changed_at": str(r[4])
                }
                for r in rows
            ]

    def get_user_application_summary(self, user_id: str = DEMO_USER_ID) -> List[Dict[str, Any]]:
        """
        Directly queries the existing MySQL VIEW `user_application_summary`.
        """
        uid = self._resolve_user_id(user_id)
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT user_id, user_name, event_type, service_name, status, created_at FROM user_application_summary WHERE user_id = :uid"),
                {"uid": uid}
            ).fetchall()

            return [
                {
                    "user_id": r[0],
                    "user_name": r[1],
                    "event_type": r[2],
                    "service_name": r[3],
                    "status": r[4],
                    "created_at": str(r[5])
                }
                for r in rows
            ]

    def get_user_journey(self, user_id: str = DEMO_USER_ID) -> List[Dict[str, Any]]:
        """
        Invokes the existing MySQL STORED PROCEDURE `get_user_journey(p_user_id)`.
        """
        uid = self._resolve_user_id(user_id)
        with self.engine.connect() as conn:
            result = conn.execute(
                text("CALL get_user_journey(:uid)"),
                {"uid": uid}
            )
            rows = result.fetchall()
            return [
                {
                    "user_name": r[0],
                    "event_type": r[1],
                    "description": r[2],
                    "service_name": r[3],
                    "status": r[4]
                }
                for r in rows
            ]

    # =========================================================================
    # Life Events & Sessions
    # =========================================================================

    def save_life_event(self, life_event: LifeEvent) -> LifeEvent:
        """
        Persist analyzed life event to MySQL `life_events` and map relevant
        services into `event_services`. Also updates document readiness baseline.
        """
        self._life_events_cache[life_event.id] = life_event

        uid = 1
        event_name = life_event.event_type.capitalize()
        desc = (life_event.raw_input or f"Life Event: {event_name}")[:500]

        try:
            with self.engine.begin() as conn:
                res = conn.execute(
                    text("INSERT INTO life_events (user_id, event_type, description) VALUES (:uid, :ev, :desc)"),
                    {"uid": uid, "ev": event_name, "desc": desc}
                )
                db_event_id = res.lastrowid

                # Link services to event in event_services
                if life_event.event_type == "relocation":
                    sids = [1, 2, 3, 4]
                elif life_event.event_type == "financial_fraud":
                    sids = [5]
                elif life_event.event_type == "marriage":
                    sids = [6, 7]
                elif life_event.event_type == "family_death":
                    sids = [8, 9]
                else:
                    sids = []

                insert_ignore_sql = "INSERT OR IGNORE" if self.engine.dialect.name == "sqlite" else "INSERT IGNORE"
                for sid in sids:
                    conn.execute(
                        text(f"{insert_ignore_sql} INTO event_services (event_id, service_id) VALUES (:eid, :sid)"),
                        {"eid": db_event_id, "sid": sid}
                    )

                # Set baseline document states for user_documents
                if life_event.event_type == "relocation":
                    # Preset demo state: 1 (Identity) & 2 (Address) Available, 3 & 4 Needed
                    if self.engine.dialect.name == "sqlite":
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 1, 'Available') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Available'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 2, 'Available') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Available'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 3, 'Needed') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Needed'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 4, 'Needed') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Needed'"))
                    else:
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 1, 'Available') ON DUPLICATE KEY UPDATE status = 'Available'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 2, 'Available') ON DUPLICATE KEY UPDATE status = 'Available'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 3, 'Needed') ON DUPLICATE KEY UPDATE status = 'Needed'"))
                        conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 4, 'Needed') ON DUPLICATE KEY UPDATE status = 'Needed'"))
                else:
                    # Non-relocation scenarios start with Needed (0 of N verified)
                    conn.execute(text("UPDATE user_documents SET status = 'Needed' WHERE user_id = 1"))
        except Exception as exc:
            logger.warning("Could not persist life_event to MySQL: %s", exc)

        return life_event

    def get_life_event(self, event_id: str) -> Optional[LifeEvent]:
        """
        Retrieve analyzed life event from cache or MySQL.
        """
        if event_id in self._life_events_cache:
            return self._life_events_cache[event_id]

        target_eid = int(event_id) if event_id.isdigit() else (int(event_id[4:]) if event_id.startswith("evt_") and event_id[4:].isdigit() else None)
        if target_eid is not None:
            try:
                with self.engine.connect() as conn:
                    row = conn.execute(
                        text("SELECT event_id, event_type, description FROM life_events WHERE event_id = :eid"),
                        {"eid": target_eid}
                    ).fetchone()
                    if row:
                        event = LifeEvent(
                            id=event_id,
                            raw_input=row[2] or "",
                            event_type=row[1].lower(),
                            message=f"Event detected: {row[1]}"
                        )
                        self._life_events_cache[event_id] = event
                        return event
            except Exception as exc:
                logger.warning("Error fetching life event from MySQL: %s", exc)

        return None

    def get_latest_life_event(self) -> Optional[LifeEvent]:
        """
        Retrieve the most recently analyzed life event.
        """
        if self._life_events_cache:
            return list(self._life_events_cache.values())[-1]

        try:
            with self.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT event_id, event_type, description FROM life_events ORDER BY event_id DESC LIMIT 1")
                ).fetchone()
                if row:
                    event = LifeEvent(
                        id=f"evt_{row[0]}",
                        raw_input=row[2] or "",
                        event_type=row[1].lower(),
                        message=f"Event detected: {row[1]}"
                    )
                    return event
        except Exception as exc:
            logger.warning("Error fetching latest life event from MySQL: %s", exc)

        return None

    def update_life_event_context(self, event_id: str, context: ContextAnswers) -> Optional[LifeEvent]:
        """
        Update context answers for an active life event.
        """
        event = self.get_life_event(event_id)
        if event:
            event.context = context
        return event

    def reset_demo_state(self) -> None:
        """
        Reset MySQL demo user records back to baseline demo state:
        - user_documents: Identity and Address Proof -> Available; Vehicle Reg & PDS -> Needed
        - applications: 1 -> Completed, 2 -> Under Review, 3 -> Action Required, 4 -> Not Started
        Note: The MySQL trigger `application_status_update` will automatically record
        any status transitions in `application_status_history`.
        """
        self._life_events_cache.clear()

        try:
            with self.engine.begin() as conn:
                # Reset demo user documents
                if self.engine.dialect.name == "sqlite":
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 1, 'Available') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Available'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 2, 'Available') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Available'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 3, 'Needed') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Needed'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 4, 'Needed') ON CONFLICT(user_id, document_id) DO UPDATE SET status = 'Needed'"))
                else:
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 1, 'Available') ON DUPLICATE KEY UPDATE status = 'Available'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 2, 'Available') ON DUPLICATE KEY UPDATE status = 'Available'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 3, 'Needed') ON DUPLICATE KEY UPDATE status = 'Needed'"))
                    conn.execute(text("INSERT INTO user_documents (user_id, document_id, status) VALUES (1, 4, 'Needed') ON DUPLICATE KEY UPDATE status = 'Needed'"))

                # Reset demo applications
                conn.execute(text("UPDATE applications SET status = 'Completed' WHERE user_id = 1 AND service_id = 1"))
                conn.execute(text("UPDATE applications SET status = 'Under Review' WHERE user_id = 1 AND service_id = 2"))
                conn.execute(text("UPDATE applications SET status = 'Action Required' WHERE user_id = 1 AND service_id = 3"))
                conn.execute(text("UPDATE applications SET status = 'Not Started' WHERE user_id = 1 AND service_id = 4"))
        except Exception as exc:
            logger.warning("Error resetting MySQL demo state: %s", exc)
