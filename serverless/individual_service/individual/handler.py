import json
import os, sys, inspect
# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# Use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../server")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../server/bb_server")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from swagger_server.models.individual import Individual

import logging

import datetime

from backbone_server.controllers.individual_controller import IndividualController

from util.response_util import create_response

individual_controller = IndividualController()

def create_individual(event, context):

    user = event['requestContext']['authorizer']['principalId']

    individual = Individual.from_dict(json.loads(event["body"]))

    value, retcode = individual_controller.create_individual(individual, user,
                                                             individual_controller.authorizer(event['requestContext']['authorizer'])) # noqa: E501

    return create_response(event, retcode, value)


def delete_individual(event, context):

    user = event['requestContext']['authorizer']['principalId']

    if 'pathParameters' in event:
        individual_id = event["pathParameters"]["individual_id"]

    value, retcode = individual_controller.delete_individual(individual_id, user,
                                                             individual_controller.authorizer(event['requestContext']['authorizer']))

    return create_response(event, retcode, value)


def download_individual(event, context):

    user = event['requestContext']['authorizer']['principalId']

    if 'pathParameters' in event:
        individual_id = event["pathParameters"]["individual_id"]

    value, retcode = individual_controller.download_individual(individual_id, user,
                                                               individual_controller.authorizer(event['requestContext']['authorizer']))

    return create_response(event, retcode, value)


def download_individuals(event, context):

    user = event['requestContext']['authorizer']['principalId']

    start = None
    count = None
    search_filter = None

    if 'queryStringParameters' in event and event["queryStringParameters"]:
        if 'start' in event["queryStringParameters"]:
            start = int(event["queryStringParameters"]["start"])
        if 'count' in event["queryStringParameters"]:
            count = int(event["queryStringParameters"]["count"])
        if 'search_filter' in event['queryStringParameters']:
            search_filter = event["queryStringParameters"]["search_filter"]

    value, retcode = individual_controller.download_individuals(search_filter, start,
                                                                count, user,
                                                                individual_controller.authorizer(event['requestContext']['authorizer']))

    return create_response(event, retcode, value)

def download_individuals_by_attr(event, context):

    user = event['requestContext']['authorizer']['principalId']

    if 'pathParameters' in event:
        prop_name = event["pathParameters"]["prop_name"]
        prop_value = event["pathParameters"]["prop_value"]

    study_name = None
    if 'queryStringParameters' in event and event["queryStringParameters"]:
        if 'study_name' in event["queryStringParameters"]:
            study_name = event["queryStringParameters"]["study_name"]

    value, retcode = individual_controller.download_individuals_by_attr(prop_name,
                                                                        prop_value,
                                                                        study_name,
                                                                        user,
                                                                        individual_controller.authorizer(event['requestContext']['authorizer']))


    return create_response(event, retcode, value)

def update_individual(event, context):

    user = event['requestContext']['authorizer']['principalId']

    if 'pathParameters' in event:
        individual_id = event["pathParameters"]["individual_id"]

    individual = Individual.from_dict(json.loads(event["body"]))

    value, retcode = individual_controller.update_location(individual_id, individual,
                                                           user,
                                                           individual_controller.authorizer(event['requestContext']['authorizer']))

    return create_response(event, retcode, value)


def merge_individuals(event, context):

    user = event['requestContext']['authorizer']['principalId']

    if 'pathParameters' in event:
        into = event["pathParameters"]["into"]
        merged = event["pathParameters"]["merged"]

    value, retcode = individual_controller.merge_individuals(into,
                                                             merged,
                                                             user,
                                                             individual_controller.authorizer(event['requestContext']['authorizer']))


    return create_response(event, retcode, value)
