from app.database.db import Base, engine
from app.models.message import Message
from app.models.missing_request import MissingRequest


def init_db():
    Base.metadata.create_all(bind=engine)