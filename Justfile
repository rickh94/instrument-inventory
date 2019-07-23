branch := `git branch | /bin/grep \* | cut -d ' ' -f2 | sed s/_//g`

test:
    pipenv run pytest -p no:warnings

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

