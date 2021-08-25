branch := `git branch | grep \* | cut -d ' ' -f2 | sed s/_//g`

test:
    poetry run pytest -p no:warnings tests/

sls-test-local FUNCTION MOCK:
    poetry run sls invoke local -f {{FUNCTION}} --path {{MOCK}}


sls-test-deploy FUNCTION MOCK:
    poetry run sls invoke -f {{FUNCTION}} --path {{MOCK}}

sls-test-branch FUNCTION MOCK:
    sls invoke --stage {{branch}} -f {{FUNCTION}} --path {{MOCK}}

deploy:
    sls deploy -v --aws-s3-accelerate

deploy-prod:
    sls deploy --stage prod -v

deploy-branch:
    sls deploy --stage {{branch}} -v --aws-s3-accelerate

test-all:
    poetry run pytest -p no:warnings

delete-tables:
    aws dynamodb delete-table --table-name dev-instrument-inventory-bows
    aws dynamodb delete-table --table-name dev-instrument-inventory-strings
    aws dynamodb delete-table --table-name dev-instrument-inventory-other

create-tables:
    aws dynamodb create-table --table-name dev-instrument-inventory-bows --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3
    aws dynamodb create-table --table-name dev-instrument-inventory-strings --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3
    aws dynamodb create-table --table-name dev-instrument-inventory-other --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3

pytest-sls-remote:
    poetry run pytest -p no:warnings --remote --stage dev serverless-tests/

pytest-sls-local:
    docker-compose up -d
    sls dynamodb migrate
    DYNAMODB_HOST=http://localhost:8000 poetry run pytest -p no:warnings --stage dev serverless-tests/
    docker-compose down
