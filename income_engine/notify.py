"""Deliver the weekly digest via email (SMTP) or Slack webhook.

Configuration is read from environment variables so nothing sensitive
lives in the portfolio file:

- Email:   INCOME_SMTP_HOST, INCOME_SMTP_PORT, INCOME_SMTP_USER,
           INCOME_SMTP_PASS, INCOME_EMAIL_FROM, INCOME_EMAIL_TO
- Slack:   INCOME_SLACK_WEBHOOK
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass(frozen=True)
class DeliveryResult:
    channel: str
    ok: bool
    detail: str


def send_email(subject: str, body_markdown: str) -> DeliveryResult:
    host = os.environ.get("INCOME_SMTP_HOST")
    to_addr = os.environ.get("INCOME_EMAIL_TO")
    if not host or not to_addr:
        return DeliveryResult("email", False, "INCOME_SMTP_HOST or INCOME_EMAIL_TO missing")
    port = int(os.environ.get("INCOME_SMTP_PORT", "587"))
    user = os.environ.get("INCOME_SMTP_USER", "")
    password = os.environ.get("INCOME_SMTP_PASS", "")
    from_addr = os.environ.get("INCOME_EMAIL_FROM", user or to_addr)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body_markdown)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls(context=context)
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    except Exception as exc:
        return DeliveryResult("email", False, f"{type(exc).__name__}: {exc}")
    return DeliveryResult("email", True, f"sent to {to_addr}")


def send_slack(body_markdown: str) -> DeliveryResult:
    webhook = os.environ.get("INCOME_SLACK_WEBHOOK")
    if not webhook:
        return DeliveryResult("slack", False, "INCOME_SLACK_WEBHOOK missing")
    payload = json.dumps({"text": body_markdown}).encode()
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
    except Exception as exc:
        return DeliveryResult("slack", False, f"{type(exc).__name__}: {exc}")
    return DeliveryResult("slack", 200 <= status < 300, f"HTTP {status}")


def deliver(subject: str, body_markdown: str, channels: list[str]) -> list[DeliveryResult]:
    results: list[DeliveryResult] = []
    for channel in channels:
        if channel == "email":
            results.append(send_email(subject, body_markdown))
        elif channel == "slack":
            results.append(send_slack(body_markdown))
        else:
            results.append(DeliveryResult(channel, False, "unknown channel"))
    return results
