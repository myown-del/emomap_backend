from typing import Protocol

import httpx


class EmailSender(Protocol):
    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        ...


class EmailDeliveryError(RuntimeError):
    pass


class UnisenderEmailSender:
    def __init__(
        self,
        api_key: str | None,
        from_email: str | None,
        base_url: str,
        timeout: int = 10,
        from_name: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.from_email = from_email
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.from_name = from_name

    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        if not self.api_key or not self.from_email:
            raise EmailDeliveryError("UniSender configuration is incomplete")

        message = {
            "recipients": [{"email": to_email}],
            "subject": "Password reset code",
            "from_email": self.from_email,
            "body": {
                "plaintext": f"Your password reset code is: {code}",
                "html": (
                    "<p>Your password reset code is: "
                    f"<strong>{code}</strong></p>"
                ),
            },
        }
        if self.from_name:
            message["from_name"] = self.from_name

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
        }
        payload = {"message": message}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/email/send.json",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EmailDeliveryError(
                f"UniSender API returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise EmailDeliveryError("Failed to call UniSender API") from exc


class NoopEmailSender:
    async def send_password_reset_code(self, to_email: str, code: str) -> None:
        return
