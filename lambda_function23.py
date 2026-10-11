import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BusPassBookings")


def lambda_handler(event, context):

    try:
        # Get booking information from API request
        body = json.loads(event["body"])

        name = body["name"]
        email = body["email"]
        source = body["source"]
        destination = body["destination"]
        pass_type = body["pass_type"]

        # Price calculation
        prices = {
            "daily": 100,
            "weekly": 500,
            "monthly": 1500
        }

        if pass_type not in prices:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid pass type"
                })
            }

        price = prices[pass_type]

        # Generate unique booking ID
        booking_id = "BP-" + str(uuid.uuid4())[:8].upper()

        # Store booking in DynamoDB
        table.put_item(
            Item={
                "booking_id": booking_id,
                "name": name,
                "email": email,
                "source": source,
                "destination": destination,
                "pass_type": pass_type,
                "price": Decimal(str(price)),
                "status": "CONFIRMED"
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Bus pass booked successfully",
                "booking_id": booking_id,
                "price": price,
                "status": "CONFIRMED"
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Booking failed",
                "error": str(e)
            })
        }