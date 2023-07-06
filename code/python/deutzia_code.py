import json
import boto3
import base64
import logging
import gzip
import os
import time

# Load the exceptions for error handling
from botocore.exceptions import ClientError, ParamValidationError
s3_bucket = os.environ.get("S3_BUCKET_NAME")
s3_default_folder = os.environ.get("S3_DEFAULT_FOLDER")
s3_resource = boto3.resource('s3', region_name=os.environ.get("AWS_REGION"))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_event_source(event):

    event_source = "unknown"
    try:
        event_source = event['Records'][0]['eventSource']
    except ParamValidationError as e:
        logger.info(f"get_event_source :: ParamValidationError = {e}")
        return event_source
    except ClientError as e:
        logger.info(f"get_event_source :: ClientError = {e}")
    except Exception as e:
        # if the event source is SNS, get the event source
        # logger.info(f"get_event_source :: UnknownKeyError = {e}")
        event_source = event['Records'][0]['EventSource']

    return event_source


def save_event_to_s3(event):

    try:
        s3_object = s3_resource.Object(
            s3_bucket, f"{s3_default_folder}/{event.get('eventID')}-{str(time.time()).replace('.','-')}.json")

        response = s3_object.put(
            Body=(bytes(json.dumps(event).encode("UTF-8"))))

        return response

    except ParamValidationError as e:
        logger.info(f"Parameter validation error: {e}")
    except ClientError as e:
        logger.info(f"Client error: {e}")


def extract_date_event(event_name, request_parameters):

    if event_name == "Scan":
        request_param_out = dict(tableName=request_parameters.get("tableName"),
                                 select=request_parameters.get("select"),
                                 limit=request_parameters.get("limit"),
                                 consistentRead=request_parameters.get(
                                     "consistentRead"),
                                 returnConsumedCapacity=request_parameters.get(
                                     "returnConsumedCapacity")
                                 )
    elif event_name == "GetItem":
        request_param_out = dict(tableName=request_parameters.get("tableName"),
                                 key=";".join(
                                     [f"{key}={value}" for key, value in request_parameters.get("key").items()]),
                                 consistentRead=request_parameters.get(
                                     "consistentRead")
                                 )
    elif event_name == "PutItem":
        request_param_out = dict(tableName=request_parameters.get("tableName"),
                                 select=request_parameters.get("select"),
                                 key=";".join(
                                     [f"{key}={value}" for key, value in request_parameters.get("key").items()]),
                                 items=",".join(
                                     request_parameters.get("items")),
                                 conditionExpression=request_parameters.get(
                                     "conditionExpression"),
                                 expressionAttributeNames=";".join(
                                     [f"{key}={value}" for key, value in request_parameters.get("expressionAttributeNames").items()])
                                 )
    if event_name == "DeleteItem":
        request_param_out = dict(tableName=request_parameters.get("tableName"),
                                key=";".join([f"{key}={value}" for key, value in request_parameters.get("key").items()])
                                 )
    return request_param_out


def lambda_handler(event, context):

    logger.info(f"event :: {json.dumps(event)}")

    logger.info(f"lambda_handler :: Total Records = {len(event['Records'])}")
    if get_event_source(event) == "aws:kinesis":
        for record in event['Records']:
            try:
                compressed_payload = base64.b64decode(
                    record['kinesis']['data'])
                uncompressed_payload = gzip.decompress(compressed_payload)
                payload = json.loads(uncompressed_payload)
                for logEvent in payload["logEvents"]:
                    if logEvent['message'] == "CWL CONTROL MESSAGE: Checking health of destination Kinesis stream.":
                        pass
                    else:
                        message = json.loads(logEvent["message"])
                        logger.info(f"message : {json.dumps(message)}")
                        request_parameters = extract_date_event(message.get(
                            "eventName"), message.get("requestParameters"))
                        data_event = request_parameters.copy()
                        data_event.update(dict(
                            eventTime=message.get("eventTime"),
                            eventSource=message.get("eventSource"),
                            eventName=message.get("eventName"),
                            requestID=message.get("requestID"),
                            eventID=message.get("eventID")
                        )
                        )

                        logger.info(f"data_event :: {json.dumps(data_event)}")

                        response = save_event_to_s3(data_event)
                        logger.info(f"response :: {json.dumps(response)}")

                        if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                            raise Exception("S3 Upload failed")
                        else:
                            logger.info("Event file uploaded to S3")

            # An error occurred
            except ParamValidationError as e:
                logger.info(f"Parameter validation error: {e}")
                return {
                    "statusCode": 300,
                    "Message": f"Parameter validation error: {e}"
                }
            except ClientError as e:
                logger.info(f"Client error: {e}")
                return {
                    "statusCode": 300,
                    "Message": f"Client  error: {e}"
                }

    return {
        "statusCode": 200,
        "Message": "Success"
    }
