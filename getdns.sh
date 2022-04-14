#!/bin/bash


MYZONE="a35fd2d640be12fa6f4d3a0b6d32e444"
BEARER_TOKEN="ri3HG53W9DJahYvh5-2lVp9BAgUdoAksw5jjVhnS"
GLOBAL_API="1b6c69832c47c2e1eb45e26c4f55495c319ec"
DNS_ZONE='justgrowthrates.com'



#curl -H "Authorization: Bearer $BEARER_TOKEN" -H Content-Type:application/json -X PUT "https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records/161b5adee2300206717b251cad6641c9" -H "Content-Type: application/json" --data '{"type":"A", "name":"flywheel.justgrowthrates.com","content":"127.0.0.55","ttl":3600,"proxied":false}'

#curl -H "Authorization: Bearer $BEARER_TOKEN" -H Content-Type:application/json -X PUT "https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records/161b5adee2300206717b251cad6641c9" -H "Content-Type: application/json" --data '{"type":"A", "name":"flywheel.justgrowtherates.com","content":"127.0.0.55","ttl":3600,"proxied":false}'


curl -H "Authorization: Bearer $BEARER_TOKEN" -H Content-Type:application/json -X GET https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records | jq '.'

exit

#curl -H "Authorization: Bearer $BEARER_TOKEN" -H Content-Type:application/json -X GET https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records?type=A&name=${DNS_ZONE}&content=flywheel&proxied=undefined&page=1&per_page=100&order=type&direction=desc&match=all | jq .

#curl -H "X-Auth-Email: jouellnyc@gmail.com" -H "X-Auth-Key: $GLOBAL_API" -H "Content-Type: application/json" -X GET https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records | jq .

#curl -H "X-Auth-Email: jouellnyc@gmail.com" -H "X-Auth-Key: $GLOBAL_API" -H "Content-Type: application/json" -X GET https://api.cloudflare.com/client/v4/zones/$MYZONE/dns_records?type=A&name=${DNS_ZONE}&content=flywheel&proxied=undefined&page=1&per_page=100&order=type&direction=desc&match=all | jq .

