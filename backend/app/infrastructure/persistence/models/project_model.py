from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client = Column(String, default="")
    global_discount = Column(Numeric(10, 2), default=0)
    global_tax = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Index for sorting

    items = relationship(
        "ProjectItemModel", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectItemModel(Base):
    __tablename__ = "project_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)  # Index for JOINs
    name = Column(String, nullable=False)
    item_type = Column(String, default="")
    base_price = Column(Numeric(10, 2), default=0)
    cost_price = Column(Numeric(10, 2), default=0)
    quantity = Column(Integer, default=1)

    project = relationship("ProjectModel", back_populates="items")
