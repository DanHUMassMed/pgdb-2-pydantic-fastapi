from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
import os
from sqlalchemy import create_engine

class Base(DeclarativeBase):
    pass

class Parent(Base):
    __tablename__ = "parent_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[List["Child"]] = relationship()


class Child(Base):
    __tablename__ = "child_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
    

def create_tables():
    # Get database URL from environment variable
    DATABASE_URL = "DATABASE_URL", "postgresql://app_user:app_passw0rd@localhost/simple_test_db"
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True to see SQL commands
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

create_tables()    