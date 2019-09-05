from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import mappings

Session = None


def init(engine_uri):
    print(engine_uri)
    engine = create_engine(engine_uri)

    global Session
    Session = sessionmaker(bind=engine)

    mappings.Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
