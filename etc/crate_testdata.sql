insert into users (id, nickname) values (1, 'lumannnn');
insert into users (id, nickname) values (2, 'lui');
insert into users (id, nickname) values (3, 'albert einstein');
insert into users (id, nickname) values (4, 'nikola tesla');

insert into votes (id, up, down) values (1, 0, 0);
insert into votes (id, up, down) values (2, 0, 0);
insert into votes (id, up, down) values (3, 0, 0);
insert into votes (id, up, down) values (4, 0, 0);

insert into projects (id, initiator_id, votes_id, name) values (1, 1, 1, 'awesome project');
insert into projects (id, initiator_id, votes_id, name) values (2, 2, 2, 'brilliant project');
insert into projects (id, initiator_id, votes_id, name) values (3, 1, 3, 'e=mc^2');
insert into projects (id, initiator_id, votes_id, name) values (4, 1, 4, 'make modern technology possible');
