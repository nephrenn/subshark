-- Create a new table with the updated schema
CREATE TABLE subscription_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    billing_date DATE NOT NULL,
    notes TEXT,
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Copy data from the old table to the new one
INSERT INTO subscription_copy 
SELECT id, user_id, name, category, cost, billing_date, notes, 'monthly' as billing_cycle
FROM subscription;

-- Delete the old table
DROP TABLE subscription;

-- Rename the new table to the original name
ALTER TABLE subscription_copy RENAME TO subscription;