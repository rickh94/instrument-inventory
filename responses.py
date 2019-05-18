import json


def success(body, status_code=200):
    return build_response(status_code, body)


def failure(body, status_code=500):
    return build_response(status_code, body)


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(body),
    }
