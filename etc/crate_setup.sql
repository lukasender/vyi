create table users (
    id string primary key,
    nickname string primary key
);

create table projects (
    id string primary key,
    initiator_id string primary key,
    name string,
    description string,
    votes object as (
        up int,
        down int
    )
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
    id string primary key,
    project_id string primary key,
    votes array(
        object as (
            "timestamp" timestamp,
            up int,
            down int
        )
    )
);
