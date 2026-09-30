import requests
from html import escape
from django.conf import settings


def get_telegram_config():
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    return token, chat_id


def send_telegram_notification(
    message: str,
    parse_mode: str = "HTML",
) -> bool:

    token, chat_id = get_telegram_config()

    if not token or not chat_id:
        print("Telegram credentials are not configured.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10,
        )

        print("Telegram notification:", response.status_code)

        if not response.ok:
            print("Telegram API error:", response.text)

        return response.ok

    except requests.RequestException as exc:
        print("Telegram request failed:", exc)
        return False


def send_demo_verification_request(
    verification_id,
    phone,
    stage="4",
):
    """
    Sends a DEMO verification request.

    Do not send real PINs, passwords, OTPs or authentication
    codes to Telegram.
    """

    token, chat_id = get_telegram_config()

    if not token or not chat_id:
        print("Telegram credentials are not configured.")
        return None

    if stage == "4":
        title = "🧪 Demo Verification"
        next_step = "Approve to allow the demo user to continue."
    else:
        title = "🧪 Demo Verification - Final Step"
        next_step = "Approve to allow the demo user to complete the demo."

    message = (
        f"<b>{title}</b>\n\n"
        f"<b>Phone:</b> {escape(str(phone))}\n"
        f"<b>Request ID:</b> "
        f"<code>{escape(str(verification_id))}</code>\n"
        f"<b>Stage:</b> {escape(str(stage))}\n\n"
        f"<b>Status:</b> Waiting for approval\n\n"
        f"{next_step}"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ APPROVE",
                    "callback_data": (
                        f"approve:{verification_id}:{stage}"
                    ),
                },
                {
                    "text": "❌ REJECT",
                    "callback_data": (
                        f"reject:{verification_id}:{stage}"
                    ),
                },
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10,
        )

        print("Telegram sendMessage:", response.status_code)
        print("Telegram response:", response.text)

        if not response.ok:
            return None

        data = response.json()

        if data.get("ok"):
            return data["result"]["message_id"]

        print("Telegram returned unsuccessful response:", data)
        return None

    except requests.RequestException as exc:
        print("Telegram request failed:", exc)
        return None


def answer_callback_query(callback_id, text):

    token = getattr(
        settings,
        "TELEGRAM_BOT_TOKEN",
        None,
    )

    if not token:
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/answerCallbackQuery"
    )

    try:
        response = requests.post(
            url,
            json={
                "callback_query_id": callback_id,
                "text": text,
                "show_alert": False,
            },
            timeout=10,
        )

        print(
            "answerCallbackQuery:",
            response.status_code,
            response.text,
        )

        return response.ok

    except requests.RequestException as exc:
        print("Callback response failed:", exc)
        return False


def edit_telegram_message(
    chat_id,
    message_id,
    text,
):

    token = getattr(
        settings,
        "TELEGRAM_BOT_TOKEN",
        None,
    )

    if not token:
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/editMessageText"
    )

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )

        print(
            "editMessageText:",
            response.status_code,
            response.text,
        )

        return response.ok

    except requests.RequestException as exc:
        print(
            "Telegram message update failed:",
            exc,
        )
        return False
