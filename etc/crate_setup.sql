create table users (
    id string primary key,
    nickname string primary key
);
create table projects (
    id string primary key,
    initiator_id string primary key,
    vote_id string primary key,
    name string,
    description string
);
create table votes (
    id string primary key,
    up int,
    down int
);
