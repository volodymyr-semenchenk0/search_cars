CREATE DATABASE IF NOT EXISTS car_offers_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS customs_calculations;
DROP TABLE IF EXISTS offers;
DROP TABLE IF EXISTS engines;
DROP TABLE IF EXISTS cars;
DROP TABLE IF EXISTS ice_powertrain_details;
DROP TABLE IF EXISTS electric_powertrain_details;
DROP TABLE IF EXISTS powertrains;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE IF NOT EXISTS countries
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    code         VARCHAR(2)            DEFAULT NULL UNIQUE,
    parsing_code VARCHAR(2)            DEFAULT NULL UNIQUE,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sources
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    url           VARCHAR(255)          DEFAULT NULL,
    description   TEXT                  DEFAULT NULL,
    contact_email VARCHAR(150)          DEFAULT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS car_makes
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    country_id INT                   DEFAULT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_car_makes_country
        FOREIGN KEY (country_id) REFERENCES countries (id)
            ON DELETE SET NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS car_models
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    make_id    INT          NOT NULL,
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_car_models_make
        FOREIGN KEY (make_id) REFERENCES car_makes (id)
            ON DELETE CASCADE,
    UNIQUE KEY idx_make_model_unique (make_id, name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS fuel_types
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    key_name   VARCHAR(50)  NOT NULL UNIQUE,
    label      VARCHAR(100) NOT NULL UNIQUE,
    code       VARCHAR(10)  NOT NULL UNIQUE,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS cars
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    model_id        INT,
    production_year INT,
    body_type       VARCHAR(100)       DEFAULT NULL,
    transmission    VARCHAR(50)        DEFAULT NULL,
    drive           VARCHAR(50)        DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_cars_model
        FOREIGN KEY (model_id) REFERENCES car_models (id)
            ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE INDEX idx_cars_model_production_year ON cars (model_id, production_year);

CREATE TABLE IF NOT EXISTS powertrains
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    car_id       INT       NOT NULL UNIQUE,
    fuel_type_id INT                DEFAULT NULL,
    mileage      INT                DEFAULT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_powertrains_car
        FOREIGN KEY (car_id) REFERENCES cars (id)
            ON DELETE CASCADE,
    CONSTRAINT fk_powertrains_fuel_type
        FOREIGN KEY (fuel_type_id) REFERENCES fuel_types (id)
            ON DELETE SET NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;
CREATE INDEX idx_powertrains_fuel_type_id ON powertrains (fuel_type_id);



CREATE TABLE IF NOT EXISTS ice_powertrain_details
(
    powertrain_id    INT PRIMARY KEY,
    engine_volume_cc INT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ice_details_powertrain
        FOREIGN KEY (powertrain_id) REFERENCES powertrains (id)
            ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS electric_powertrain_details
(
    powertrain_id        INT PRIMARY KEY,
    battery_capacity_kwh DECIMAL(5, 1) DEFAULT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_electric_details_powertrain
        FOREIGN KEY (powertrain_id) REFERENCES powertrains (id)
            ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS offers
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    offer_identifier    VARCHAR(255),
    car_id              INT       NOT NULL,
    source_id           INT       NOT NULL,
    link_to_offer       TEXT      NOT NULL,
    price               DECIMAL(12, 2),
    currency            VARCHAR(3)         DEFAULT 'EUR',
    country_of_listing  VARCHAR(100)       DEFAULT NULL,
    offer_created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price_at_timestamp  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_online_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_offers_car
        FOREIGN KEY (car_id) REFERENCES cars (id)
            ON DELETE CASCADE,

    CONSTRAINT fk_offers_source
        FOREIGN KEY (source_id) REFERENCES sources (id)
            ON DELETE RESTRICT,

    UNIQUE KEY idx_unique_offer_on_source (source_id, offer_identifier)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE INDEX idx_offers_car_id ON offers (car_id);
CREATE INDEX idx_offers_source_id ON offers (source_id);
CREATE INDEX idx_offers_price ON offers (price);
CREATE INDEX idx_offers_country_of_listing ON offers (country_of_listing);

CREATE TABLE IF NOT EXISTS customs_calculations
(
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    offer_id                    INT       NOT NULL UNIQUE,
    duty_uah                    DECIMAL(12, 2)     DEFAULT NULL,
    excise_eur                  DECIMAL(12, 2)     DEFAULT NULL,
    excise_uah                  DECIMAL(12, 2)     DEFAULT NULL,
    vat_uah                     DECIMAL(12, 2)     DEFAULT NULL,
    pension_fee_uah             DECIMAL(12, 2)     DEFAULT NULL,
    customs_payments_total_uah  DECIMAL(12, 2)     DEFAULT NULL,
    final_total_without_pension DECIMAL(12, 2)     DEFAULT NULL,
    final_total                 DECIMAL(12, 2)     DEFAULT NULL,
    eur_to_uah_rate_actual      DECIMAL(10, 4)     DEFAULT NULL,

    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_customs_offer
        FOREIGN KEY (offer_id) REFERENCES offers (id)
            ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE INDEX idx_customs_offer_id ON customs_calculations (offer_id);


