from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime,Date, Boolean, Integer, Table, Column, ForeignKey, CheckConstraint, Float
from datetime import datetime, date
import random


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
)

book_categories = Table(
    "book_categories",
    Base.metadata,
    Column("book_description__id", Integer, ForeignKey("book_descriptions.id"), nullable=False),
    Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
)

class Users(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(150), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(200), nullable=False)
    phone : Mapped[str] = mapped_column(String(50),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    # Relationship with addresses
    addresses : Mapped[list["Addresses"]] = relationship("Addresses", secondary="user_addresses", back_populates="users")
    # Relationship with payments
    payments : Mapped[list["Payments"]] = relationship("Payments", back_populates="user")
    # Relationship with orders
    orders : Mapped[list["Orders"]] = relationship("Orders", back_populates="user")
    # Relationship with carts
    cart : Mapped["Carts"] = relationship("Carts", back_populates="user")
    # Relationship with reviews
    reviews : Mapped[list["Reviews"]] = relationship("Reviews", back_populates="user")
    # Relationship with favorites
    favorites : Mapped[list["Favorites"]] = relationship("Favorites", back_populates="user")


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
    # Relationship with orders
    orders : Mapped[list["Orders"]] = relationship("Orders", back_populates="address")

    
class Payments(Base):
    __tablename__ = "payments"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    card_number : Mapped[str] = mapped_column(String(20), nullable=False)
    cvv : Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_month : Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year : Mapped[int] = mapped_column(Integer, nullable=False)
    is_default : Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship with users
    user : Mapped["Users"] = relationship("Users", back_populates="payments")
    # Relationship with Orders
    orders: Mapped[list["Orders"]] = relationship("Orders", back_populates="payment")

class Orders(Base):
    __tablename__ = "orders"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    payment_id : Mapped[int] = mapped_column(Integer, ForeignKey("payments.id"), nullable=False)
    address_id : Mapped[int] = mapped_column(Integer, ForeignKey("addresses.id"), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    status : Mapped[str] = mapped_column(String(50),CheckConstraint("status IN ('Pending', 'Processing', 'Shipped', 'Cancelled', 'Returned')"), nullable=False, default="Pending")
    shipping_method : Mapped[str] = mapped_column(String(50), CheckConstraint("shipping_method IN ('Out-for-Delivery','Delivered', 'Delayed', 'Returned')"))
    subtotal : Mapped[float] = mapped_column(Float, nullable=False, default=0)
    tax : Mapped[float] = mapped_column(Float, nullable=False, default=0)
    shipping_cost : Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total : Mapped[float] = mapped_column(Float, nullable=False, default=0)

    # Relationship with user
    user : Mapped["Users"] = relationship("Users", back_populates="orders")
    # Relationship with payments
    payment : Mapped["Payments"] = relationship("Payments", back_populates="orders")
    # Relationship with addresses
    address : Mapped["Addresses"] = relationship("Addresses", back_populates="orders")
    # Relationship with order_books
    order_books : Mapped[list["Order_books"]] = relationship("Order_books", back_populates="order")
    
    
class Carts(Base):
    __tablename__ = "carts"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    # Relationship with users
    user : Mapped["Users"] = relationship("Users", back_populates="cart")
    # Relationship with cart_books
    cart_books : Mapped[list["Cart_books"]] = relationship("Cart_books", back_populates="cart") 


class Reviews(Base):
    __tablename__ = "reviews"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_description_id : Mapped[int] = mapped_column(ForeignKey("book_descriptions.id"), nullable=False)
    rating : Mapped[float] = mapped_column(Float,nullable=False, default=0)
    comment : Mapped[str] = mapped_column(String)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    # Relationship with user
    user : Mapped["Users"] = relationship("Users", back_populates="reviews")
    # Relationship with book_descriptions
    book_description : Mapped["Book_descriptions"] = relationship("Book_descriptions", back_populates="reviews")

class Favorites(Base):
    __tablename__ = "favorites"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_description_id : Mapped[int] = mapped_column(ForeignKey("book_descriptions.id"), nullable=False)

    # Relationship with user
    user : Mapped["Users"] = relationship("Users", back_populates="favorites")
    # Relationship with book_descriptions
    book_description : Mapped["Book_descriptions"] = relationship("Book_descriptions", back_populates="favorites")

class Book_descriptions(Base):
    __tablename__ = "book_descriptions"

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(400), nullable=False)
    subtitle : Mapped[str] = mapped_column(String(500), nullable=False)
    author : Mapped[str] = mapped_column(String(200), nullable=False)
    publisher : Mapped[str] = mapped_column(String(200), nullable=False)
    published_date : Mapped[date] = mapped_column(Date)
    description : Mapped[str] = mapped_column(String(1500), nullable=False)
    isbn : Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    page_count : Mapped[int] = mapped_column(Integer, nullable=False)
    image_link : Mapped[str] = mapped_column(String(900), nullable=False)
    language : Mapped[str] = mapped_column(String(9), nullable=False)
    price: Mapped[float] = mapped_column(Float,nullable=False, default=lambda: round(random.uniform(12.00, 52.00), 2))
    stock_quantity : Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    # Relationship with favorites
    favorites : Mapped[list["Favorites"]] = relationship("Favorites", back_populates="book_description")
    # Relationship with reviews
    reviews : Mapped[list["Reviews"]] = relationship("Reviews", back_populates="book_description")
    # Relationship with cart_books
    cart_books : Mapped[list["Cart_books"]] = relationship("Cart_books", back_populates="book_description")
    # Relationship with order_books
    order_books : Mapped[list["Order_books"]] = relationship("Order_books", back_populates="book_description")
    # Relationship with categories
    categories : Mapped[list["Categories"]] = relationship("Categories",secondary="book_categories",back_populates="book_descriptions")

class Cart_books(Base):
    __tablename__ = "cart_books"

    id : Mapped[int] = mapped_column(primary_key=True)
    cart_id : Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    book_description_id : Mapped[int] = mapped_column(ForeignKey("book_descriptions.id"), nullable=False)
    quantity : Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationship with carts
    cart : Mapped["Carts"] = relationship("Carts", back_populates="cart_books")
    # Relationship with book_descriptions
    book_description : Mapped["Book_descriptions"] = relationship("Book_descriptions", back_populates="cart_books")

class Order_books(Base):
    __tablename__ = "order_books"

    id : Mapped[int] = mapped_column(primary_key=True)
    order_id : Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    book_description_id : Mapped[int] = mapped_column(ForeignKey("book_descriptions.id"), nullable=False)
    quantity : Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationship with carts
    order : Mapped["Orders"] = relationship("Orders", back_populates="order_books")
    # Relationship with book_descriptions
    book_description : Mapped["Book_descriptions"] = relationship("Book_descriptions", back_populates="order_books")

class Categories(Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(250), nullable=False)

    # Relationship with book_description
    book_descriptions : Mapped[list["Book_descriptions"]] = relationship("Book_descriptions",secondary="book_categories",back_populates="categories")