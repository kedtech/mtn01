from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = "Set Telegram webhook to the current site URL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help="Full webhook URL (optional). Example: https://mtn01.onrender.com/telegram/callback/",
        )

    def handle(self, *args, **options):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)

        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set in settings/environment"))
            return

        # Default URL if not provided
        webhook_url = options.get("url") or "https://mtn01.onrender.com/telegram/callback/"

        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        payload = {"url": webhook_url}

        try:
            response = requests.post(api_url, json=payload, timeout=15)
            data = response.json()

            if data.get("ok"):
                self.stdout.write(self.style.SUCCESS(f"Webhook set successfully to: {webhook_url}"))
            else:
                self.stderr.write(self.style.ERROR(f"Failed to set webhook: {data}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
