-- Consolidated migration from Alembic migrations
-- To be used with Supabase CLI

-- Initial migration (c178b6ce7f3b)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_unique ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username_unique ON users (username);

-- uploads table (2391fbb8337c)
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    file_path VARCHAR NOT NULL,
    file_name VARCHAR NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_uploads_id ON uploads (id);

-- Add file_size to uploads (5ad5170c537b)
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS file_size BIGINT NOT NULL;

-- orders table (b18df65bc4c6)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    financial_status VARCHAR,
    paid_at TIMESTAMPTZ,
    fulfillment_status VARCHAR,
    fulfilled_at TIMESTAMPTZ,
    accepts_marketing VARCHAR,
    currency VARCHAR,
    subtotal VARCHAR,
    shipping VARCHAR,
    taxes VARCHAR,
    total VARCHAR,
    discount_code VARCHAR,
    discount_amount VARCHAR,
    shipping_method VARCHAR,
    created_at TIMESTAMPTZ,
    billing_name VARCHAR,
    billing_street VARCHAR,
    billing_address1 VARCHAR,
    billing_address2 VARCHAR,
    billing_company VARCHAR,
    billing_city VARCHAR,
    billing_zip VARCHAR,
    billing_province VARCHAR,
    billing_country VARCHAR,
    billing_phone VARCHAR,
    shipping_name VARCHAR,
    shipping_street VARCHAR,
    shipping_address1 VARCHAR,
    shipping_address2 VARCHAR,
    shipping_company VARCHAR,
    shipping_city VARCHAR,
    shipping_zip VARCHAR,
    shipping_province VARCHAR,
    shipping_country VARCHAR,
    shipping_phone VARCHAR,
    cancelled_at TIMESTAMPTZ,
    payment_method VARCHAR,
    payment_reference VARCHAR,
    refunded_amount VARCHAR,
    vendor VARCHAR,
    outstanding_balance VARCHAR,
    employee VARCHAR,
    location VARCHAR,
    device_id VARCHAR,
    order_id VARCHAR,
    tags VARCHAR,
    risk_level VARCHAR,
    source VARCHAR,
    phone VARCHAR,
    receipt_number VARCHAR,
    duties VARCHAR,
    billing_province_name VARCHAR,
    shipping_province_name VARCHAR,
    payment_id VARCHAR,
    payment_terms_name VARCHAR,
    next_payment_due_at TIMESTAMPTZ,
    payment_references VARCHAR,
    user_id INTEGER NOT NULL REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_orders_id ON orders (id);

-- line_items table (37c485a93436)
CREATE TABLE IF NOT EXISTS line_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    lineitem_quantity INTEGER,
    lineitem_name VARCHAR,
    lineitem_price VARCHAR,
    lineitem_compare_at_price VARCHAR,
    lineitem_sku VARCHAR,
    lineitem_requires_shipping VARCHAR,
    lineitem_taxable VARCHAR,
    lineitem_fulfillment_status VARCHAR,
    lineitem_discount VARCHAR
);

CREATE INDEX IF NOT EXISTS ix_line_items_id ON line_items (id);
CREATE INDEX IF NOT EXISTS ix_orders_order_id ON orders (order_id);

-- Add variant_id to line_items (f1553950c6ff)
ALTER TABLE line_items ADD COLUMN IF NOT EXISTS variant_id VARCHAR;

-- Add upload_id to orders (0084c7558f73)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS upload_id INTEGER REFERENCES uploads(id);

-- Add status to uploads (22dba09067a0)
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'pending';

-- Convert various VARCHAR columns to Numeric in orders (0d0c13f1fbcf)
ALTER TABLE line_items 
    ALTER COLUMN lineitem_discount TYPE NUMERIC(12, 2) 
    USING NULLIF(lineitem_discount, '')::NUMERIC(12, 2);

ALTER TABLE orders 
    ALTER COLUMN subtotal TYPE NUMERIC(12, 2) 
    USING NULLIF(subtotal, '')::NUMERIC(12, 2),
    ALTER COLUMN shipping TYPE NUMERIC(12, 2) 
    USING NULLIF(shipping, '')::NUMERIC(12, 2),
    ALTER COLUMN taxes TYPE NUMERIC(12, 2) 
    USING NULLIF(taxes, '')::NUMERIC(12, 2),
    ALTER COLUMN total TYPE NUMERIC(12, 2) 
    USING NULLIF(total, '')::NUMERIC(12, 2),
    ALTER COLUMN discount_amount TYPE NUMERIC(12, 2) 
    USING NULLIF(discount_amount, '')::NUMERIC(12, 2),
    ALTER COLUMN refunded_amount TYPE NUMERIC(12, 2) 
    USING NULLIF(refunded_amount, '')::NUMERIC(12, 2),
    ALTER COLUMN outstanding_balance TYPE NUMERIC(12, 2) 
    USING NULLIF(outstanding_balance, '')::NUMERIC(12, 2),
    ALTER COLUMN duties TYPE NUMERIC(12, 2) 
    USING NULLIF(duties, '')::NUMERIC(12, 2);

-- Create index on orders (0d0c13f1fbcf)
CREATE INDEX IF NOT EXISTS idx_orders_user_created ON orders (user_id, created_at);

-- Add columns to uploads (5b09189040db)
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS total_rows INTEGER;
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS records_processed INTEGER;

-- Add job_id to uploads (31a87cee84b2)
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS job_id VARCHAR;

-- Convert lineitem_price and lineitem_compare_at_price to Numeric (a76a60be9b13)
ALTER TABLE line_items 
    ALTER COLUMN lineitem_price TYPE NUMERIC(12, 2) 
    USING CASE WHEN lineitem_price ~ '^[0-9]+(\.[0-9]+)?$' THEN lineitem_price::NUMERIC(12, 2) ELSE NULL END,
    ALTER COLUMN lineitem_compare_at_price TYPE NUMERIC(12, 2) 
    USING CASE WHEN lineitem_compare_at_price ~ '^[0-9]+(\.[0-9]+)?$' THEN lineitem_compare_at_price::NUMERIC(12, 2) ELSE NULL END;
