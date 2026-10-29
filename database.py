import os
from sqlalchemy import create_engine, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL не найден в .env")

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_header: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    task_description: Mapped[str] = mapped_column(String(225))
    addition_time: Mapped[object] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(225), nullable=False)

def create_tables():
    Base.metadata.create_all(engine)

def add_data(data):
    session = Session()
    session.add(data)
    session.commit()