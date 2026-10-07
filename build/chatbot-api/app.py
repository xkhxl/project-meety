import os
import json
import boto3
from shared.responses import success_response, error_response

lex_client = boto3.client("lexv2-runtime")

BOT_ID = os.environ["LEX_BOT_ID"]
BOT_ALIAS_ID = os.environ["LEX_BOT_ALIAS_ID"]
LOCALE_ID = os.environ.get("LEX_LOCALE_ID", "en_US")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        message = body.get("message")

        if not message:
            return error_response(400, "Missing message")

        response = lex_client.recognize_text(
            botId=BOT_ID,
            botAliasId=BOT_ALIAS_ID,
            localeId=LOCALE_ID,
            sessionId="meety-session",
            text=message
        )

        messages = response.get("messages", [])
        if not messages:
            return error_response(500, "No response from chatbot")

        bot_response = messages[0].get("content", "No chatbot response available")
        return success_response(200, {"botResponse": bot_response})
    except Exception as e:
        print(f"ERROR in chatbot-api: {str(e)}")
        return error_response(500, "Failed to process chatbot request")