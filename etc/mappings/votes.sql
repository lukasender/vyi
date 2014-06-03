CREATE TABLE votes (
    project_id string,
    up int,
    down int
) CLUSTERED BY (project_id)
