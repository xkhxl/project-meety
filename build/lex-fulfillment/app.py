import os
import uuid
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def get_session_attributes(intent_request):
    session_state = intent_request.get("sessionState", {})
    return session_state.get("sessionAttributes", {})


def get_slots(intent_request):
    return intent_request.get("sessionState", {}).get("intent", {}).get("slots", {})


def get_slot(intent_request, slot_name):
    slots = get_slots(intent_request)
    slot = slots.get(slot_name)

    if slot and slot.get("value"):
        return slot["value"].get("interpretedValue")
    return None


def close(intent_request, session_attributes, fulfillment_state, message):
    intent = intent_request["sessionState"]["intent"]
    intent["state"] = fulfillment_state

    return {
        "sessionState": {
            "sessionAttributes": session_attributes,
            "dialogAction": {
                "type": "Close"
            },
            "intent": intent
        },
        "messages": [message]
    }


def calculate_end_time(start_time_str, duration_minutes):
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = (
        datetime.combine(datetime.today(), start_time) +
        timedelta(minutes=duration_minutes)
    ).time()
    return end_time.strftime("%H:%M")


def check_meeting_slot(proposed_date, proposed_start, proposed_duration):
    proposed_date_obj = datetime.strptime(proposed_date, "%Y-%m-%d").date()
    proposed_start_time = datetime.strptime(proposed_start, "%H:%M").time()
    proposed_end_time = (
        datetime.combine(proposed_date_obj, proposed_start_time) +
        timedelta(minutes=proposed_duration)
    ).time()

    start_time_str = proposed_start_time.strftime("%H:%M")
    end_time_str = proposed_end_time.strftime("%H:%M")

    response = table.query(
        IndexName="StatusIndex",
        KeyConditionExpression=Key("status").eq("approved") & Key("date").eq(proposed_date_obj.isoformat()),
        FilterExpression=(
            (Attr("startTime").gt(start_time_str) & Attr("startTime").lt(end_time_str)) |
            Attr("startTime").eq(start_time_str) |
            (Attr("endTime").gt(start_time_str) & Attr("endTime").lt(end_time_str))
        )
    )

    return len(response.get("Items", [])) == 0


def create_meeting(intent_request):
    session_attributes = get_session_attributes(intent_request)

    attendee_name = get_slot(intent_request, "FullName")
    meeting_date = get_slot(intent_request, "MeetingDate")
    meeting_time = get_slot(intent_request, "MeetingTime")
    meeting_duration = get_slot(intent_request, "MeetingDuration")
    attendee_email = get_slot(intent_request, "AttendeeEmail")

    if not all([attendee_name, meeting_date, meeting_time, meeting_duration, attendee_email]):
        return close(
            intent_request,
            session_attributes,
            "Failed",
            {
                "contentType": "PlainText",
                "content": "Missing required meeting details."
            }
        )

    duration_int = int(meeting_duration)
    end_time = calculate_end_time(meeting_time, duration_int)
    is_available = check_meeting_slot(meeting_date, meeting_time, duration_int)
    is_conflict = not is_available

    current_timestamp = datetime.utcnow().isoformat()

    item = {
        "meetingId": str(uuid.uuid4()),
        "attendeeName": attendee_name,
        "email": attendee_email,
        "date": meeting_date,
        "startTime": meeting_time,
        "endTime": end_time,
        "duration": duration_int,
        "status": "pending",
        "isConflict": is_conflict,
        "createdAt": current_timestamp,
        "updatedAt": current_timestamp,
        "source": "lex"
    }

    table.put_item(Item=item)

    if is_conflict:
        message_text = (
            f"Thank you {attendee_name}. Your meeting request for {meeting_date} from "
            f"{meeting_time} to {end_time} has been created, but there is a scheduling conflict. "
            f"It is pending review."
        )
    else:
        message_text = (
            f"Thank you {attendee_name}. Your meeting request for {meeting_date} from "
            f"{meeting_time} to {end_time} has been created. Have a nice day!"
        )

    return close(
        intent_request,
        session_attributes,
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": message_text
        }
    )


def lambda_handler(event, context):
    print("Lex fulfillment event:", event)

    intent_name = event.get("sessionState", {}).get("intent", {}).get("name")

    if intent_name == "BookMeeting":
        return create_meeting(event)

    return close(
        event,
        get_session_attributes(event),
        "Failed",
        {
            "contentType": "PlainText",
            "content": f"Unsupported intent: {intent_name}"
        }
    )