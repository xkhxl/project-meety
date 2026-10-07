import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from shared.responses import success_response, error_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    start_date_str = params.get("startDate")
    end_date_str = params.get("endDate")

    if not start_date_str or not end_date_str:
        return error_response(400, "Missing required query parameters: startDate and endDate")

    try:
        start_date = datetime.fromisoformat(start_date_str) - timedelta(days=1)
        end_date = datetime.fromisoformat(end_date_str)

        response = table.query(
            IndexName="StatusIndex",
            KeyConditionExpression=Key("status").eq("approved") & Key("date").between(
                start_date.date().isoformat(),
                end_date.date().isoformat()
            )
        )

        return success_response(200, response.get("Items", []))
    except Exception as e:
        print(f"ERROR in get-meetings: {str(e)}")
        return error_response(500, "Failed to fetch meetings")