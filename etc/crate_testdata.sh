curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"elon_musk","balance":10000.00}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"albert_einstein","balance":10000.00}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"nikola_tesla","balance":10000.00}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/users/register -d '{"nickname":"lovelace","balance":10000.00}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"awesome project", "initiator": "elon_musk"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"brilliant project", "initiator": "lovelace"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"e=mc^2", "initiator": "albert_einstein"}'
echo ""
curl -XPOST -H "Content-Type: application/json" http://localhost:9100/projects/add -d '{"name":"make modern technology possible", "initiator": "nikola_tesla"}'
echo ""
