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
create table stats (
    id string primary key,
    project_id string primary key,
    votes object as (
        up int,
        down int
    )
);
