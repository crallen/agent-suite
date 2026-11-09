CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_email TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'canceled'))
);
