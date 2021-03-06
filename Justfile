branch := `git branch | /bin/grep \* | cut -d ' ' -f2 | sed s/_//g`

test:
    pipenv run pytest -p no:warnings tests/

sls-test-local FUNCTION MOCK:
    pipenv run sls invoke local -f {{FUNCTION}} --path {{MOCK}}


sls-test-deploy FUNCTION MOCK:
    pipenv run sls invoke -f {{FUNCTION}} --path {{MOCK}}

sls-test-branch FUNCTION MOCK:
    sls invoke --stage {{branch}} -f {{FUNCTION}} --path {{MOCK}}

deploy:
    sls deploy -v --aws-s3-accelerate

deploy-prod:
    sls deploy --stage prod -v

deploy-branch:
    sls deploy --stage {{branch}} -v --aws-s3-accelerate

test-all:
    pipenv run pytest -p no:warnings

delete-tables:
    aws dynamodb delete-table --table-name dev-instrument-inventory-bows
    aws dynamodb delete-table --table-name dev-instrument-inventory-strings
    aws dynamodb delete-table --table-name dev-instrument-inventory-other

create-tables:
    aws dynamodb create-table --table-name dev-instrument-inventory-bows --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3
    aws dynamodb create-table --table-name dev-instrument-inventory-strings --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3
    aws dynamodb create-table --table-name dev-instrument-inventory-other --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3

pytest-sls-remote:
    pipenv run pytest -p no:warnings --remote --stage dev serverless-tests/

pytest-sls-local:
    serverless dynamodb start &
    serverless dynamodb migrate
    DYNAMODB_HOST=http://localhost:8000 pipenv run pytest -p no:warnings --stage dev serverless-tests/
    kill -9 `ps -ef | grep "[D]ynamoDBLocal.jar" | awk '{print $2}'`
