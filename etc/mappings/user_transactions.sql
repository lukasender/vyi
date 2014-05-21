create table user_transactions (
    id string,
    user_id string primary key,
    transaction_id string primary key,
    amount double primary key,
    "timestamp" timestamp,
    state string
) partitioned by (user_id)
