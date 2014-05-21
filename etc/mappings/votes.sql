create table votes (
    project_id string,
    up int,
    down int
) clustered by (project_id)
