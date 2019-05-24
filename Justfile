test:
    pipenv run pytest

sls-test-local FUNCTION MOCK:
    pipenv run sls invoke local -f {{FUNCTION}} --path {{MOCK}}


sls-test-deploy FUNCTION MOCK:
    pipenv run sls invoke -f {{FUNCTION}} --path {{MOCK}}

deploy:
    sls deploy -v

deploy-prod:
    sls deploy --stage prod -v
