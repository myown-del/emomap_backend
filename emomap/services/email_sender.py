from email.message import EmailMessage
from typing import Protocol

import aiosmtplib


class EmailSender(Protocol):
    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        pass


class SMTPEmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        from_email: str | None,
        use_tls: bool = False,
        use_starttls: bool = True,
        timeout: int = 10,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
        self.use_starttls = use_starttls
        self.timeout = timeout

    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        if not self.host or not self.from_email:
            raise ValueError("SMTP configuration is incomplete")

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = "Password reset code"
        message.set_content(f"Your password reset code is: {code}")

        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls,
            start_tls=self.use_starttls,
            timeout=self.timeout,
        )


class NoopEmailSender:
    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        return
