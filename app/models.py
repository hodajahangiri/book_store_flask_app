from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, Boolean, Integer, Table, Column, ForeignKey
from datetime import datetime


# Create Base Class
class Base(DeclarativeBase):
    pass

# instantiate SQLAlchemy db
db = SQLAlchemy(model_class=Base)


user_addresses = Table(
    "user_addresses",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("address_id", Integer, ForeignKey("addresses.id"), nullable=False),
    Column("is_default", Boolean, default=False)
)

class Users(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(150), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(500), nullable=False)
    password : Mapped[str] = mapped_column(String(200), nullable=False)
    phone : Mapped[str] = mapped_column(String(50),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    # Relationship with addresses
    addresses : Mapped[list["Addresses"]] = relationship("Addresses", secondary="user_addresses", back_populates="users")

    # Relationship with payments
    payments : Mapped[list["Payments"]] = relationship("Payments", back_populates="user")

class Addresses(Base):
    __tablename__ = "addresses"

    id : Mapped[int] = mapped_column(primary_key=True)
    line1 : Mapped[str] = mapped_column(String(300), nullable=False)
    line2 : Mapped[str] = mapped_column(String(300), nullable=True)
    number :  Mapped[int] = mapped_column(Integer, nullable=True)
    city : Mapped[str] = mapped_column(String(100), nullable=False)
    state : Mapped[str] = mapped_column(String(100), nullable=False)
    country : Mapped[str] = mapped_column(String(100), nullable=False)
    zipcode : Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationship with users
    users : Mapped[list["Users"]] = relationship("Users", secondary="user_addresses", back_populates="addresses")

    
class Payments(Base):
    __tablename__ = "payments"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    card_number : Mapped[str] = mapped_column(String(20), nullable=False)
    cvv : Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_month : Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year : Mapped[int] = mapped_column(Integer, nullable=False)
    is_default : Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship with user
    user : Mapped["Users"] = relationship("Users", back_populates="payments")


