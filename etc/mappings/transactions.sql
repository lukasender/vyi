CREATE TABLE transactions (
    id string PRIMARY KEY,
    sender string PRIMARY KEY,
    recipient string,
    amount double,
    type string,
    state string,
    "timestamp" timestamp,
    processed_by string
) CLUSTERED BY (sender)
