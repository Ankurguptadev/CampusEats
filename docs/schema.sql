CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE addresses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    address         VARCHAR(200) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    zip             VARCHAR(20)  NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE restaurants (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(150) NOT NULL,
    location        VARCHAR(100) NOT NULL,
    status        BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE menu_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id   INTEGER NOT NULL,
    name            VARCHAR(150) NOT NULL,
    price           DECIMAL(8,2) NOT NULL,
    description     VARCHAR(500) NOT NULL,
    available       BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);



CREATE TABLE carts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id         INTEGER NOT NULL,
    menu_item_id    INTEGER NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (cart_id) REFERENCES carts(id)
);

CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL, 
    address_id      INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'placed',
    total           DECIMAL(8,2) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    menu_item_id    INTEGER NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price_at_order  DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);


CREATE TABLE transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    amount          DECIMAL(8,2) NOT NULL,
    payment_method  VARCHAR(30) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE refunds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id  INTEGER NOT NULL,
    amount          DECIMAL(8,2) NOT NULL,
    reason          VARCHAR(200),
    status          VARCHAR(20) NOT NULL DEFAULT 'initiated',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);


CREATE TABLE riders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'available',
    curr_location   VARCHAR(200) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE assignments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    rider_id        INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'assigned',
    assigned_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    est_minutes     INTEGER NOT NULL, 
    delivered_at    TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES riders(id)
);



CREATE TABLE messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    order_id        INTEGER,
    type            VARCHAR(30) NOT NULL,
    message         TEXT NOT NULL,
    sent_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);