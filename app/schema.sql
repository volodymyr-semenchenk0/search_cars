
CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identifier VARCHAR(100),
    make VARCHAR(100),
    model VARCHAR(100),
    year INT,
    body_type VARCHAR(100),
    engine_type VARCHAR(50),
    engine_volume FLOAT,
    transmission VARCHAR(50),
    drive VARCHAR(50),
    mileage INT,
    country VARCHAR(100),
    price DECIMAL(12,2),
    customs_uah DECIMAL(12,2),
    final_price_uah DECIMAL(12,2),
    link TEXT,
    source VARCHAR(50),
    battery_capacity_kwh FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
x