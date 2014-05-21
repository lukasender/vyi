create table comments (
    project_id string,
    user_id string,
    comment string,
    "timestamp" timestamp
) clustered by (user_id) with (refresh_interval=2500)
