def lambda_handler(event, context):
    print("Lex fulfillment event:", event)
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": event["sessionState"]["intent"]["name"],
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Lex fulfillment placeholder response."
            }
        ]
    }