import africastalking
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


username = "sandbox"   # use sandbox
api_key = "atsk_ed7b0ce2fdc054cea840bee5096711d3f35669e86cb4f187f142cabf2db93228d1e2cec3"

africastalking.initialize(username, api_key)

sms = africastalking.SMS


def send_bulk_sms(phone_numbers, message):
    try:
        response = sms.send(message, phone_numbers)
        print("Africa's Talking response:", response)
        return response
        # response = sms.send("Steve says good morning, ")
        # print(response)
        # return response

    except Exception as e:
        error_message = str(e)
        print("SMS sending failed:", error_message)

        return {
            "status": "error",
            "message": error_message
        }