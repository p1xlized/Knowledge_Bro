from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False allows FastAPI's async execution to safely use SQLite
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Creates the SQLite database file and tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a DB session per request."""
    with Session(engine) as session:
        yield session
