CREATE DATABASE IF NOT EXISTS campuseats;
USE campuseats;

DROP TABLE IF EXISTS dishes;

CREATE TABLE dishes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  price      INT          NOT NULL,          
  available  BOOLEAN      NOT NULL DEFAULT TRUE 
);

INSERT INTO dishes (name, price, available) VALUES
  ('Veg Thali',    80, TRUE),
  ('Masala Dosa',  60, TRUE),
  ('Cold Coffee',  50, FALSE),
  ('Samosa',   20, TRUE);
