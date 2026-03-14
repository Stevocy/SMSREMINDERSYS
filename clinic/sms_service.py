# # sms_service.py



# sms_service.py
import re
import africastalking
import ssl
import requests


#ssl._create_default_https_context = ssl._create_unverified_context

# Africa's Talking credentials
USERNAME = "sandbox"
API_KEY = "atsk_ed7b0ce2fdc054cea840bee5096711d3f35669e86cb4f187f142cabf2db93228d1e2cec3"

# Initialize SDK
africastalking.initialize(USERNAME, API_KEY)
sms = africastalking.SMS


# -------------------------------
# Phone Utilities
# -------------------------------

def normalize_phone_number(phone_number: str) -> str:
    """
    Convert Kenyan numbers to E.164 format
    Example:
    0712345678 -> +254712345678
    712345678  -> +254712345678
    254712345678 -> +254712345678
    """

    phone_number = phone_number.strip()

    if phone_number.startswith("+"):
        return phone_number

    if phone_number.startswith("0"):
        return "+254" + phone_number[1:]

    if phone_number.startswith("254"):
        return "+" + phone_number

    if phone_number.startswith("7"):
        return "+254" + phone_number

    return phone_number


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate E.164 format
    """
    pattern = re.compile(r"^\+[1-9]\d{6,14}$")
    return bool(pattern.match(phone_number))


# -------------------------------
# Send Single SMS
# -------------------------------

# def send_sms(phone_number: str, message: str) -> bool:

#     phone_number = normalize_phone_number(phone_number)

#     if not validate_phone_number(phone_number):
#         print("Invalid phone number:", phone_number)
#         return False

#     try:
#         response = sms.send(message, [phone_number])

#         print("Africa's Talking response:", response)

#         recipients = response.get("SMSMessageData", {}).get("Recipients", [])

#         return any(r.get("status") == "Success" for r in recipients)

#     except Exception as e:
#         print("SMS sending failed:", str(e))
#         return False


import requests

def send_sms(phone_number: str, message: str) -> bool:
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {"apiKey": API_KEY, "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "username": USERNAME,
        "to": phone_number,
        "message": message,
    }
    try:
        r = requests.post(url, headers=headers, data=data, verify=False)  # remove verify=False later
        print("Direct requests status:", r.status_code, r.text)
        return r.status_code == 201
    except Exception as e:
        print("Direct requests failed:", e)
        return False
    
# -------------------------------
# Send Bulk SMS
# -------------------------------

def send_bulk_sms(phone_numbers, message):

    valid_numbers = []

    for number in phone_numbers:
        n = normalize_phone_number(number)
        if validate_phone_number(n):
            valid_numbers.append(n)

    if not valid_numbers:
        print("No valid phone numbers provided")
        return False

    try:
        response = sms.send(message, valid_numbers)

        print("Africa's Talking response:", response)

        recipients = response.get("SMSMessageData", {}).get("Recipients", [])

        return any(r.get("status") == "Success" for r in recipients)

    except Exception as e:
        print("Bulk SMS failed:", str(e))
        return False



















# import logging
# import re
# from django.conf import settings

# logger = logging.getLogger(__name__)


# class SMSProvider:
#     """Abstract base SMS provider."""
#     def send(self, phone_numbers, message):
#         raise NotImplementedError


# # ----------------------------------------------------
# # MOCK PROVIDER (development mode)
# # ----------------------------------------------------

# class MockProvider(SMSProvider):
#     def send(self, phone_numbers, message):
#         if isinstance(phone_numbers, str):
#             phone_numbers = [phone_numbers]

#         for number in phone_numbers:
#             logger.info(f"[MOCK SMS] {number} -> {message}")

#         print("--------------------------------------------------")
#         print("[MOCK SMS GATEWAY]")
#         print("Recipients:", phone_numbers)
#         print("Message:", message)
#         print("--------------------------------------------------")

#         return True


# # ----------------------------------------------------
# # AFRICAS TALKING PROVIDER
# # ----------------------------------------------------

# class AfricasTalkingProvider(SMSProvider):

#     def __init__(self, username, api_key, sender_id=None):
#         self.username = username
#         self.api_key = api_key
#         self.sender_id = sender_id

#         try:
#             import africastalking

#             africastalking.initialize(username, api_key)
#             self._sms = africastalking.SMS

#             logger.info("Africa's Talking initialized")

#         except Exception as e:
#             logger.error("Africa's Talking initialization failed")
#             logger.exception(e)
#             self._sms = None

#     def send(self, phone_numbers, message):

#         if not self._sms:
#             logger.error("SMS provider not ready")
#             return False

#         if isinstance(phone_numbers, str):
#             phone_numbers = [phone_numbers]

#         try:

#             response = self._sms.send(
#                 message,
#                 phone_numbers
#             )
#             print("AT RESPONSE:", response)

#             logger.info(f"Africa's Talking response: {response}")

#             recipients = response.get("SMSMessageData", {}).get("Recipients", [])

#             success = any(r.get("status") == "Success" for r in recipients)

#             return success

#         except Exception as e:
#             logger.exception("SMS sending failed")
#             return False


# # ----------------------------------------------------
# # PHONE UTILITIES
# # ----------------------------------------------------

# def normalize_phone_number(phone_number: str) -> str:
#     """
#     Convert Kenyan numbers to E.164
#     """

#     phone_number = phone_number.strip()

#     if phone_number.startswith("+"):
#         return phone_number

#     if phone_number.startswith("0"):
#         return "+254" + phone_number[1:]

#     if phone_number.startswith("254"):
#         return "+" + phone_number

#     if phone_number.startswith("7"):
#         return "+254" + phone_number

#     return phone_number


# def validate_phone_number(phone_number: str) -> bool:
#     """
#     Validate E.164 numbers
#     """

#     pattern = re.compile(r"^\+[1-9]\d{6,14}$")
#     return bool(pattern.match(phone_number))


# # ----------------------------------------------------
# # PROVIDER SELECTOR
# # ----------------------------------------------------

# def get_sms_provider():

#     provider = "africastalking"

#     if provider == "africastalking":
#         return AfricasTalkingProvider(
#             username="sandbox",
#             api_key="atsk_ed7b0ce2fdc054cea840bee5096711d3f35669e86cb4f187f142cabf2db93228d1e2cec3"
#         )

#     return MockProvider()


# # ----------------------------------------------------
# # SEND SMS
# # ----------------------------------------------------

# def send_sms(phone_number: str, message: str):

#     phone_number = normalize_phone_number(phone_number)

#     if not validate_phone_number(phone_number):
#         logger.error(f"Invalid number: {phone_number}")
#         return False

#     provider = get_sms_provider()

#     return provider.send(phone_number, message)


# # ----------------------------------------------------
# # BULK SMS
# # ----------------------------------------------------

# def send_bulk_sms(phone_numbers, message):

#     provider = get_sms_provider()

#     normalized = []

#     for number in phone_numbers:
#         n = normalize_phone_number(number)

#         if validate_phone_number(n):
#             normalized.append(n)

#     if not normalized:
#         logger.error("No valid phone numbers provided")
#         return False

#     return provider.send(normalized, message)


# """
# my sandbox api key for testing purposes = atsk_ed7b0ce2fdc054cea840bee5096711d3f35669e86cb4f187f142cabf2db93228d1e2cec3
# """