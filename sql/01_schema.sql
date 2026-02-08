-- Create optimized table structure
CREATE TABLE online_retail (
    invoice_no VARCHAR(10),
    stock_code VARCHAR(20),
    description VARCHAR(100),
    quantity INT,
    invoice_date TIMESTAMP,
    unit_price DECIMAL(10,2),
    customer_id VARCHAR(10),
    country VARCHAR(50),
    total_amount DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Create indexes for performance
CREATE INDEX idx_customer ON online_retail(customer_id);
CREATE INDEX idx_date ON online_retail(invoice_date);
CREATE INDEX idx_invoice ON online_retail(invoice_no);