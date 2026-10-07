import os
import boto3
from boto3.dynamodb.conditions import Key
from shared.responses import success_response, error_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        response = table.query(
            IndexName="StatusIndex",
            KeyConditionExpression=Key("status").eq("pending")
        )
        return success_response(200, response.get("Items", []))
    except Exception as e:
        print(f"ERROR in get-pending-meetings: {str(e)}")
        return error_response(500, "Failed to fetch pending meetings")