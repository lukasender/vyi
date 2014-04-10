curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"lumannnn"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"lui"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"albert_einstein"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"nickola_tesla"}'

curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"awesome project", "initiator": "lumannnn"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"brilliant project", "initiator": "lui"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"e=mc^2", "initiator": "albert_einstein"}'
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"make modern technology possible", "initiator": "nickola_tesla"}'
