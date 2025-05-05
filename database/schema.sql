
CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(100),
    model VARCHAR(100),
    year INT,
    body_type VARCHAR(100),
    engine_type VARCHAR(50),
    engine_volume FLOAT,
    transmission VARCHAR(50),
    drive VARCHAR(50),
    mileage INT,
    country VARCHAR(100),
    price DECIMAL,
    customs_uah DECIMAL,
    final_price_uah DECIMAL,
    link TEXT,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
