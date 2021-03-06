import base64
import json
import ujson

import logging

def get_body(event):

    body = event["body"]

    if "isBase64Encoded" in event and event["isBase64Encoded"]:
        bdy = base64.b64decode(body)
        return ujson.loads(bdy)
    else:
        return ujson.loads(body)

def get_user(event):

    user = None

    if 'authorizer' in event['requestContext']:
        user = event['requestContext']['authorizer']['principalId']

    return user

def get_auths(controller, event):

    return controller.authorizer(event['requestContext']['authorizer'])
