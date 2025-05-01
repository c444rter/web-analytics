# backend/db/models.py

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, BigInteger, Numeric, Index
from sqlalchemy.orm import relationship
from .base import Base

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)  # Primary Key for the Upload
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String, default="pending", nullable=False)

    # Columns to track upload progress
    total_rows = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)

    # Define the relationships
    user = relationship("User", back_populates="uploads")
    orders = relationship("Order", back_populates="upload")

    # Define the job_id as an optional field since it is for background processing
    job_id = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    uploads = relationship("Upload", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    order_id = Column(String, index=True)   # Shopify order ID
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    financial_status = Column(String)
    paid_at = Column(DateTime)
    fulfillment_status = Column(String)
    fulfilled_at = Column(DateTime)
    accepts_marketing = Column(String)
    currency = Column(String)

    # Changed from String to Numeric for better analytics
    subtotal = Column(Numeric(12, 2))
    shipping = Column(Numeric(12, 2))
    taxes = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))

    discount_code = Column(String)
    discount_amount = Column(Numeric(12, 2))
    shipping_method = Column(String)
    created_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    payment_method = Column(String)
    payment_reference = Column(String)
    refunded_amount = Column(Numeric(12, 2))
    vendor = Column(String)
    outstanding_balance = Column(Numeric(12, 2))
    employee = Column(String)
    location = Column(String)
    device_id = Column(String)
    tags = Column(String)
    risk_level = Column(String)
    source = Column(String)
    phone = Column(String)
    receipt_number = Column(String)
    duties = Column(Numeric(12, 2))
    billing_name = Column(String)
    billing_street = Column(String)
    billing_address1 = Column(String)
    billing_address2 = Column(String)
    billing_company = Column(String)
    billing_city = Column(String)
    billing_zip = Column(String)
    billing_province = Column(String)
    billing_country = Column(String)
    billing_phone = Column(String)
    billing_province_name = Column(String)
    shipping_name = Column(String)
    shipping_street = Column(String)
    shipping_address1 = Column(String)
    shipping_address2 = Column(String)
    shipping_company = Column(String)
    shipping_city = Column(String)
    shipping_zip = Column(String)
    shipping_province = Column(String)
    shipping_country = Column(String)
    shipping_phone = Column(String)
    shipping_province_name = Column(String)
    payment_id = Column(String)
    payment_terms_name = Column(String)
    next_payment_due_at = Column(DateTime)
    payment_references = Column(String)

    user = relationship("User", back_populates="orders")
    upload = relationship("Upload", back_populates="orders")
    line_items = relationship("LineItem", back_populates="order", cascade="all, delete-orphan")

    # Example index for queries that filter by user + created_at
    __table_args__ = (
        Index("idx_orders_user_created", "user_id", "created_at"),
    )

class LineItem(Base):
    __tablename__ = "line_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    lineitem_quantity = Column(Integer)
    lineitem_name = Column(String)
    lineitem_price = Column(Numeric(12, 2))  # Changed from String to Numeric
    lineitem_compare_at_price = Column(Numeric(12, 2), nullable=True)  # Changed from String to Numeric
    lineitem_sku = Column(String)
    lineitem_requires_shipping = Column(String)
    lineitem_taxable = Column(String)
    lineitem_fulfillment_status = Column(String)
    lineitem_discount = Column(Numeric(12, 2))
    variant_id = Column(String)

    order = relationship("Order", back_populates="line_items")
