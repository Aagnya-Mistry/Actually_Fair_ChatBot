from app.database.db import SessionLocal
from app.models.message import Message


class SessionService:
    def save_message(self, session_id: str, role: str, content: str):
        db = SessionLocal()

        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content
            )

            db.add(message)
            db.commit()
        finally:
            db.close()

    def get_messages(self, session_id: str):
        db = SessionLocal()

        try:
            messages = (
                db.query(Message)
                .filter(Message.session_id == session_id)
                .order_by(Message.id)
                .all()
            )

            return [
                {
                    "role": message.role,
                    "content": message.content
                }
                for message in messages
            ]
        finally:
            db.close()


session_service = SessionService()