CREATE TABLE transactions (
    id string PRIMARY KEY,
    sender string PRIMARY KEY,
    receiver string,
    amount double,
    type string,
    state string,
    "timestamp" timestamp,
    processed_by string
) CLUSTERED BY (sender)
