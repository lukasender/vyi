curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"lumannnn"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"luibär"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"albert_einstein"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"nikola_tesla"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"awesome project", "initiator": "lumannnn"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"brilliant project", "initiator": "luibär"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"e=mc^2", "initiator": "albert_einstein"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"make modern technology possible", "initiator": "nikola_tesla"}'
echo ""
