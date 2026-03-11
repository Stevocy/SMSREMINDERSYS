#sms_service.py
import logging
import re
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSProvider:
    """Abstract base SMS provider."""
    def send(self, phone_number, message):
        raise NotImplementedError

#CSKnIRTcC

class MockProvider(SMSProvider):
    """Development/testing provider — prints to console, never calls a real API."""
    def send(self, phone_number, message):
        logger.info(f"Mock SMS to {phone_number}: {message}")
        print("--------------------------------------------------")
        print(f"[MOCK GATEWAY] Sending to: {phone_number}")
        print(f"Message: {message}")
        print("--------------------------------------------------")
        return True


class AfricasTalkingProvider(SMSProvider):
    """Production provider using the Africa's Talking API."""
    def __init__(self, username, api_key, sender_id=None):
        self.username = username
        self.api_key = api_key
        self.sender_id = sender_id

        try:
            import africastalking
            africastalking.initialize(username, api_key)
            self._sms = africastalking.SMS
            self._ready = True
            logger.info("Africa's Talking SDK initialized successfully")
        except ImportError:
            logger.warning(
                "Package 'africastalking' not installed. "
                "Run: pip install africastalking. Falling back to mock."
            )
            self._ready = False
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking: {e}")
            self._ready = False

    def send(self, phone_number, message):
        if not self._ready:
            logger.error("Africa's Talking not initialized — message NOT sent.")
            return False

        try:
            recipients = [phone_number]  # list, even for one number

            kwargs = {
                "message": message,
                "recipients": recipients,
            }
            if self.sender_id:
                kwargs["senderId"] = self.sender_id   # optional short code / alphanumeric

            # Optional: channel='dnd' or other advanced params

            response = self._sms.send(**kwargs)

            # Example response: {'SMSMessageData': {'Recipients': [{'status': 'Success', 'number': '...'}]}}
            recipients_info = response.get("SMSMessageData", {}).get("Recipients", [])
            
            if recipients_info and recipients_info[0].get("status") == "Success":
                logger.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                error_msg = recipients_info[0].get("statusCode") or recipients_info[0].get("message") or "Unknown error"
                logger.error(f"Africa's Talking failed for {phone_number}: {error_msg} - Full response: {response}")
                return False

        except Exception as e:
            logger.exception(f"Africa's Talking exception while sending to {phone_number}")
            return False
        


def validate_phone_number(phone_number: str) -> bool:
    """
    Validates phone number in E.164 format (example: +254712345678)
    """
    pattern = re.compile(r"^\+[1-9]\d{6,14}$")
    return bool(pattern.match(phone_number))
def normalize_phone_number(phone_number: str) -> str:
    """
    Convert Kenyan phone numbers to E.164 format.
    Examples:
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

def get_sms_provider():
    """
    Returns the correct SMS provider based on settings
    """
    provider = getattr(settings, "SMS_PROVIDER", "mock")

    if provider == "africastalking":
        return AfricasTalkingProvider(
            username=getattr(settings, "AT_USERNAME", ""),
            api_key=getattr(settings, "AT_API_KEY", ""),
            sender_id=getattr(settings, "AT_SENDER_ID", None)
        )

    return MockProvider()


# def send_sms(phone_number: str, message: str) -> bool:
#     """
#     Validates number and sends SMS
#     """
#     if not validate_phone_number(phone_number):
#         logger.error(f"Invalid phone number: {phone_number}")
#         return False

#     provider = get_sms_provider()
#     return provider.send(phone_number, message)
def send_sms(phone_number: str, message: str) -> bool:
    phone_number = normalize_phone_number(phone_number)

    if not validate_phone_number(phone_number):
        logger.error(f"Invalid phone number format: {phone_number}")
        return False

    provider = get_sms_provider()
    return provider.send(phone_number, message)


"""
my sandbox api key for testing purposes = atsk_ed7b0ce2fdc054cea840bee5096711d3f35669e86cb4f187f142cabf2db93228d1e2cec3
"""