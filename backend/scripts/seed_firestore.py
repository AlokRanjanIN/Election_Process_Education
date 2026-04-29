"""
Firestore Seed Script — Seeds timelines and user_sessions collections.

Usage:
  python -m scripts.seed_firestore
  python -m scripts.seed_firestore --dry-run
"""

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def seed_timelines(db, dry_run: bool = False) -> int:
    """Seed the timelines collection from JSON data."""
    data_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "seed_timelines.json",
    )

    if not os.path.exists(data_file):
        logger.error("Seed file not found: %s", data_file)
        return 0

    with open(data_file, "r", encoding="utf-8") as f:
        timelines = json.load(f)

    count = 0
    collection_ref = db.collection(settings.COLLECTION_TIMELINES)

    for timeline in timelines:
        doc_id = f"{timeline['state_code']}_{timeline['constituency_id']}"

        if dry_run:
            logger.info(
                "[DRY RUN] Would seed: %s -> %d events",
                doc_id,
                len(timeline.get("events", [])),
            )
        else:
            collection_ref.document(doc_id).set(timeline)
            logger.info(
                "Seeded: %s -> %d events",
                doc_id,
                len(timeline.get("events", [])),
            )
        count += 1

    return count


def seed_sample_sessions(db, dry_run: bool = False) -> int:
    """Seed sample user sessions for testing."""
    sessions = [
        {
            "session_id": "test-session-001",
            "current_state": "INIT",
            "last_updated": "2024-01-01T00:00:00Z",
            "context": {},
        },
        {
            "session_id": "test-session-002",
            "current_state": "FORM_DOWNLOADED",
            "last_updated": "2024-01-01T00:00:00Z",
            "context": {"required_form": "Form 6"},
        },
    ]

    collection_ref = db.collection(settings.COLLECTION_USER_SESSIONS)
    count = 0

    for session in sessions:
        if dry_run:
            logger.info(
                "[DRY RUN] Would seed session: %s (state=%s)",
                session["session_id"],
                session["current_state"],
            )
        else:
            collection_ref.document(session["session_id"]).set(session)
            logger.info(
                "Seeded session: %s (state=%s)",
                session["session_id"],
                session["current_state"],
            )
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Seed Firestore collections with initial data."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be seeded without writing to Firestore.",
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN mode — no data will be written.")
        # Create a mock for dry run
        class MockCollection:
            def document(self, _):
                return self
            def set(self, _):
                pass
        class MockDB:
            def collection(self, _):
                return MockCollection()
        db = MockDB()
    else:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {"projectId": settings.GCP_PROJECT_ID})
        db = firestore.client()

    timeline_count = seed_timelines(db, dry_run=args.dry_run)
    session_count = seed_sample_sessions(db, dry_run=args.dry_run)

    logger.info(
        "Seeding complete: %d timelines, %d sessions",
        timeline_count,
        session_count,
    )


if __name__ == "__main__":
    main()
