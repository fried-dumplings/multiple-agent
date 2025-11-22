from typing import Optional

from agno.tools import Toolkit
from agno.utils.log import log_info, logger


class CEmailTools(Toolkit):
    def __init__(
        self,
        receiver_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_passkey: Optional[str] = None,
        sender_smtp_server: Optional[str] = None,
        sender_smtp_port: Optional[int] = None,
        enable_email_user: bool = True,
        all: bool = False,
        **kwargs,
    ):
        self.receiver_email: Optional[str] = receiver_email
        self.sender_name: Optional[str] = sender_name
        self.sender_email: Optional[str] = sender_email
        self.sender_passkey: Optional[str] = sender_passkey

        self.sender_smtp_server: Optional[str] = sender_smtp_server
        self.sender_smtp_port: Optional[int] = sender_smtp_port

        tools = []
        if all or enable_email_user:
            tools.append(self.email_user)

        # Call superclass with tools list
        super().__init__(name="email_tools", tools=tools, **kwargs)

    def email_user(self, subject: str, body: str) -> str:
        """Emails the user with the given subject and body.

        :param subject: The subject of the email.
        :param body: The body of the email.
        :return: "success" if the email was sent successfully, "error: [error message]" otherwise.
        """
        try:
            import smtplib
            from email.message import EmailMessage
        except ImportError:
            logger.error("`smtplib` not installed")
            raise

        if not self.receiver_email:
            return "error: No receiver email provided"
        if not self.sender_name:
            return "error: No sender name provided"
        if not self.sender_email:
            return "error: No sender email provided"
        if not self.sender_passkey:
            return "error: No sender passkey provided"
        if not self.sender_smtp_server:
            return "error: No sender SMTP server provided"
        if not self.sender_smtp_port:
            return "error: No sender SMTP port provided"

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = self.receiver_email
        msg.set_content(body)

        log_info(f"Sending Email to {self.receiver_email}")
        try:
            # with smtplib.SMTP_SSL(self.sender_smtp_server, self.sender_smtp_port) as smtp:
            #     smtp.login(self.sender_email, self.sender_passkey)
            #     smtp.send_message(msg)
            server = smtplib.SMTP(self.sender_smtp_server, self.sender_smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_passkey)  
            server.sendmail(self.sender_email, [self.receiver_email], msg.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")
            logger.error(f"Error sending email: {e}")
            return f"error: {e}"
        return "email sent successfully"
