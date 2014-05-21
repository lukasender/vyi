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
)
