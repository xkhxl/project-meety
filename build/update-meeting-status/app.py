import os
import json
import boto3
from datetime import datetime, timezone
from shared.responses import success_response, error_response
from shared.validation import require_fields

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        missing = require_fields(body, ["meetingId", "newStatus"])

        if missing:
            return error_response(400, f"Missing required fields: {', '.join(missing)}")

        meeting_id = body["meetingId"]
        new_status = body["newStatus"]

        if new_status not in ["approved", "rejected"]:
            return error_response(400, "newStatus must be approved or rejected")

        updated_at = datetime.now(timezone.utc).isoformat()

        table.update_item(
            Key={"meetingId": meeting_id},
            UpdateExpression="SET #status = :new_status, updatedAt = :updated_at",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":new_status": new_status,
                ":updated_at": updated_at
            }
        )

        return success_response(200, {"message": "Meeting status updated", "updatedAt": updated_at})
    except Exception as e:
        print(f"ERROR in update-meeting-status: {str(e)}")
        return error_response(500, "Failed to update meeting status")