#!/bin/bash

m2m_token=72e59d2df0ab0cf82b7ab44ec8144f169786c70cea882de6d4f99ef89ebb2c14
url=http://applb-zemrmdoib3shy.westeurope.cloudapp.azure.com
options=-s

# list companies
curl $options  --request GET \
	--url ${url}/api/v1/companies/ \
	--header 'authorization: token '"$m2m_token" \
	--header 'content-type: application/json' | jq "."

# add company
curl $options  --request POST \
	--url ${url}/api/v1/companies/ \
	--header 'authorization: token '"$m2m_token" \
	--header 'content-type: application/json' \
	--data '{"uuid":"gs1se:0002","country":"AD","company":"some test company"}'

# list prefixes
curl $options  --request GET \
	--url ${url}/api/v1/prefixes/ \
	--header 'authorization: token '"$m2m_token" \
	--header 'content-type: application/json' | jq "."



# add prefix
curl $options  --request POST \
	--url ${url}/api/v1/companies/gs1se:0001/prefixes/ \
	--header 'authorization: Token '"$m2m_token" \
	--header 'content-type: application/json' \
	--data '{"prefix":"73512345"}' | jq "."


# update prefix
curl $options  --request PATCH \
	--url ${url}/api/v1/prefixes/73512345/ \
	--header 'authorization: Token '"$m2m_token" \
	--header 'content-type: application/json' \
	--data '{"description":"baz"}' | jq "."

# list users
curl $verbose  --request GET \
	--url ${url}/api/v1/users/ \
	--header 'authorization: Token '"$m2m_token" \
	--header 'content-type: application/json' | jq "."


# add user
curl $verbose  --request POST \
	--url ${url}/api/v1/companies/gs1se:0002/users/ \
	--header 'authorization: Token '"$m2m_token" \
	--header 'content-type: application/json' \
	--data '{"email":"test22896@test.com","uid":"foo-22889"}'

exit

# delete company
curl $verbose --request DELETE \
	--url ${url}/api/v1/companies/gs1se:0001/ \
        --header 'authorization: Token '"$m2m_token" \
	--header 'content-type: application/json' \
