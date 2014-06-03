CREATE TABLE comments (
    project_id string,
    user_id string,
    comment string,
    "timestamp" timestamp
) CLUSTERED BY (user_id) WITH (refresh_interval=2500)
