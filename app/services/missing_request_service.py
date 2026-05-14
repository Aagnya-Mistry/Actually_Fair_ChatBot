from app.database.db import SessionLocal
from app.models.missing_request import MissingRequest


class MissingRequestService:
    def save_request(self, session_id: str, query: str):
        db = SessionLocal()

        try:
            missing_request = MissingRequest(
                session_id=session_id,
                query=query
            )

            db.add(missing_request)
            db.commit()
        finally:
            db.close()


missing_request_service = MissingRequestService()