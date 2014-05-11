create table users (
    id string primary key,
    nickname string primary key,
    balance double
);

create table projects (
    id string primary key,
    initiator_id string primary key,
    name string,
    description string,
    votes object as (
        up int,
        down int
    ),
    balance double
);

create table transactions (
    id string primary key,
    "timestamp" timestamp,
    sender string,
    receiver string,
    amount double,
    type string,
    state string
);

create table votes (
    project_id string,
    up int,
    down int
) clustered by (project_id);

create table comments (
    project_id string,
    user_id string,
    comment string,
    "timestamp" timestamp
) clustered by (user_id) with (refresh_interval=2500);

create table stats (
    project_id string,
    "timestamp" timestamp,
    up int,
    down int
);
