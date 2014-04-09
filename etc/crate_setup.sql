create table user (id int primary key, nickname string);
create table project (id int primary key, initiator_id int, name string, description string, votes_id int);
create table votes (id int primary key, up int, down int);

insert into user (id, nickname) values (1, 'lumannnn');
insert into user (id, nickname) values (2, 'lui');
insert into user (id, nickname) values (3, 'albert einstein');
insert into user (id, nickname) values (4, 'nikola tesla');

insert into votes (id, up, down) values (1, 0, 0);
insert into votes (id, up, down) values (2, 0, 0);
insert into votes (id, up, down) values (3, 0, 0);
insert into votes (id, up, down) values (4, 0, 0);

insert into project (id, initiator_id, name, votes_id) values (1, 1, 'awesome project', 1);
insert into project (id, initiator_id, name, votes_id) values (2, 2, 'brilliant project', 2);
insert into project (id, initiator_id, name, votes_id) values (3, 1, 'e=mc^2', 3);
insert into project (id, initiator_id, name, votes_id) values (4, 1, 'make modern technology possible', 4);
