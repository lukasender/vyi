create table transactions (
    id string primary key,
    sender string primary key,
    receiver string,
    amount double,
    type string,
    state string,
    "timestamp" timestamp,
    processed_by string
) clustered by (sender)
