@csrf_exempt
def telegram_callback_view(request):
    """
    Receives Telegram webhook updates.

    Handles:

        approve:<verification_id>:<stage>
        reject:<verification_id>:<stage>
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    try:
        update = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400,
        )

    print("===== TELEGRAM WEBHOOK =====")
    print(update)
    print("============================")

    callback = update.get("callback_query")

    # Telegram may send other types of updates.
    if not callback:
        return JsonResponse({"ok": True})

    callback_id = callback.get("id")
    callback_data = callback.get("data", "")

    if not callback_id:
        return JsonResponse(
            {"error": "Missing callback ID"},
            status=400,
        )

    print("CALLBACK DATA:", callback_data)

    parts = callback_data.split(":")

    if len(parts) != 3:
        answer_callback_query(
            callback_id,
            "Invalid button request.",
        )

        return JsonResponse(
            {"error": "Invalid callback data"},
            status=400,
        )

    action = parts[0]
    verification_id = parts[1]
    stage = parts[2]

    if action not in {"approve", "reject"}:
        answer_callback_query(
            callback_id,
            "Unknown action.",
        )

        return JsonResponse(
            {"error": "Unknown action"},
            status=400,
        )

    try:
        verification_id = int(verification_id)
    except ValueError:
        answer_callback_query(
            callback_id,
            "Invalid verification ID.",
        )

        return JsonResponse(
            {"error": "Invalid verification ID"},
            status=400,
        )

    try:
        verification = DemoVerification.objects.get(
            id=verification_id
        )
    except DemoVerification.DoesNotExist:

        answer_callback_query(
            callback_id,
            "Verification request no longer exists.",
        )

        return JsonResponse(
            {"error": "Verification not found"},
            status=404,
        )

    callback_message = callback.get("message")

    if not callback_message:
        answer_callback_query(
            callback_id,
            "Telegram message not found.",
        )

        return JsonResponse(
            {"error": "Message missing"},
            status=400,
        )

    chat = callback_message.get("chat", {})
    message_id = callback_message.get("message_id")
    chat_id = chat.get("id")

    stage_text = (
        "Demo Verification"
        if stage == "4"
        else "Demo Final Verification"
    )

    # ----------------------------------------
    # APPROVE
    # ----------------------------------------

    if action == "approve":

        verification.status = "approved"
        verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        answer_callback_query(
            callback_id,
            "✅ Demo verification approved.",
        )

        if chat_id and message_id:
            edit_telegram_message(
                chat_id,
                message_id,
                (
                    f"🧪 <b>{stage_text}</b>\n\n"
                    f"<b>Phone:</b> "
                    f"{escape(str(verification.phone))}\n"
                    f"<b>Request ID:</b> "
                    f"<code>{verification.id}</code>\n"
                    f"<b>Status:</b> ✅ Approved"
                ),
            )

        return JsonResponse({"ok": True})

    # ----------------------------------------
    # REJECT
    # ----------------------------------------

    if action == "reject":

        verification.status = "rejected"
        verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        answer_callback_query(
            callback_id,
            "❌ Demo verification rejected.",
        )

        if chat_id and message_id:
            edit_telegram_message(
                chat_id,
                message_id,
                (
                    f"🧪 <b>{stage_text}</b>\n\n"
                    f"<b>Phone:</b> "
                    f"{escape(str(verification.phone))}\n"
                    f"<b>Request ID:</b> "
                    f"<code>{verification.id}</code>\n"
                    f"<b>Status:</b> ❌ Rejected"
                ),
            )

        return JsonResponse({"ok": True})

    return JsonResponse({"ok": True})
