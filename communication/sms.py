from django.conf import settings


def send_sms(to_phone, message):
    """Send an SMS via Twilio. Returns (ok, sid_or_error)."""
    try:
        from twilio.rest import Client
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            return False, "Twilio not configured"
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=to_phone)
        return True, msg.sid
    except Exception as e:
        return False, str(e)
