CREATE DATABASE IF NOT EXISTS car_search_db;
USE car_search_db;

CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50),
    model VARCHAR(50),
    year VARCHAR(10),
    price VARCHAR(20),
    mileage VARCHAR(20),
    link VARCHAR(255),
    source VARCHAR(50)
);
