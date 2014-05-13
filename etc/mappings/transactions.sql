create table transactions (
    id string primary key,
    "timestamp" timestamp,
    sender string,
    receiver string,
    amount double,
    type string,
    state string
)
