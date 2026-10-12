import json
import boto3
import uuid
from decimal import Decimal


# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("BusPassBookings")


def lambda_handler(event, context):

    # Find which HTTP method was used
    http_method = event.get("httpMethod")

    # --------------------------------
    # POST - CREATE NEW BOOKING
    # --------------------------------

    if http_method == "POST":

        try:

            # Read data sent from webpage
            body = json.loads(event.get("body", "{}"))

            name = body.get("name")
            email = body.get("email")
            source = body.get("source")
            destination = body.get("destination")
            pass_type = body.get("pass_type")

            # Check required fields
            if not all([
                name,
                email,
                source,
                destination,
                pass_type
            ]):

                return {
                    "statusCode": 400,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "message": "All fields are required"
                    })
                }

            # --------------------------------
            # PRICE CALCULATION
            # --------------------------------

            prices = {
                "daily": 100,
                "weekly": 500,
                "monthly": 1500
            }

            if pass_type not in prices:

                return {
                    "statusCode": 400,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "message": "Invalid pass type"
                    })
                }

            price = prices[pass_type]

            # --------------------------------
            # GENERATE UNIQUE BOOKING ID
            # --------------------------------

            booking_id = "BP-" + str(uuid.uuid4())[:8].upper()

            # --------------------------------
            # SAVE TO DYNAMODB
            # --------------------------------

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

            # --------------------------------
            # RETURN SUCCESS RESPONSE
            # --------------------------------

            return {

                "statusCode": 200,

                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },

                "body": json.dumps({

                    "message":
                    "Bus pass booked successfully",

                    "booking_id":
                    booking_id,

                    "name":
                    name,

                    "source":
                    source,

                    "destination":
                    destination,

                    "pass_type":
                    pass_type,

                    "price":
                    price,

                    "status":
                    "CONFIRMED"
                })
            }

        except Exception as e:

            return {

                "statusCode": 500,

                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },

                "body": json.dumps({

                    "message":
                    "Booking failed",

                    "error":
                    str(e)
                })
            }

    # --------------------------------
    # GET - CHECK EXISTING BOOKING
    # --------------------------------

    elif http_method == "GET":

        try:

            # Get booking ID from URL
            query_parameters = event.get(
                "queryStringParameters"
            ) or {}

            booking_id = query_parameters.get(
                "booking_id"
            )

            # Check booking ID
            if not booking_id:

                return {

                    "statusCode": 400,

                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },

                    "body": json.dumps({

                        "message":
                        "Please provide booking_id"
                    })
                }

            # --------------------------------
            # SEARCH DYNAMODB
            # --------------------------------

            response = table.get_item(

                Key={
                    "booking_id": booking_id
                }
            )

            # Get item
            item = response.get("Item")

            # --------------------------------
            # BOOKING NOT FOUND
            # --------------------------------

            if not item:

                return {

                    "statusCode": 404,

                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },

                    "body": json.dumps({

                        "message":
                        "Booking not found"
                    })
                }

            # --------------------------------
            # BOOKING FOUND
            # --------------------------------

            # Convert Decimal values
            item["price"] = int(item["price"])

            return {

                "statusCode": 200,

                "headers": {

                    "Access-Control-Allow-Origin": "*",

                    "Content-Type":
                    "application/json"
                },

                "body": json.dumps({

                    "message":
                    "Booking found",

                    "booking":
                    item
                })
            }

        except Exception as e:

            return {

                "statusCode": 500,

                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },

                "body": json.dumps({

                    "message":
                    "Unable to retrieve booking",

                    "error":
                    str(e)
                })
            }

    # --------------------------------
    # INVALID METHOD
    # --------------------------------

    else:

        return {

            "statusCode": 405,

            "headers": {
                "Access-Control-Allow-Origin": "*"
            },

            "body": json.dumps({

                "message":
                "Method not allowed"
            })
        }