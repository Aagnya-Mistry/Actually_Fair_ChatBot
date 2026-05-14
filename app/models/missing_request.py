from sqlalchemy import Column, Integer, String, Text

from app.database.db import Base


class MissingRequest(Base):
    __tablename__ = "missing_requests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    query = Column(Text, nullable=False)