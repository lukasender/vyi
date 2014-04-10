create table users (
    id int primary key,
    nickname string primary key
);
create table projects (
    id int primary key,
    initiator_id int primary key,
    votes_id int primary key,
    name string,
    description string
);
create table votes (
    id int primary key,
    up int,
    down int
);
