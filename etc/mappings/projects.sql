CREATE TABLE projects (
    id string PRIMARY KEY,
    initiator_id string PRIMARY KEY,
    name string,
    description string,
    votes object AS (
        up int,
        down int
    ),
    balance double
)
