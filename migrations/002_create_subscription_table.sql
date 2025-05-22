CREATE TABLE subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    billing_date DATE NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);