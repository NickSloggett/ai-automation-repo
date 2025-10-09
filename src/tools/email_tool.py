"""Email automation tool."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import structlog

from .base import Tool, ToolResult, ToolConfig
from ..config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class EmailTool(Tool):
    """Tool for sending and managing emails."""

    def __init__(self, config: ToolConfig):
        """Initialize email tool.

        Args:
            config: Tool configuration
        """
        super().__init__(config)
        self.logger = logger.bind(tool="email")

    async def execute(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html: bool = False,
        from_email: str = None,
        cc_emails: List[str] = None,
        bcc_emails: List[str] = None,
        attachments: List[str] = None,
    ) -> ToolResult:
        """Send an email.

        Args:
            to_emails: Recipient email addresses
            subject: Email subject
            body: Email body
            html: Send as HTML email
            from_email: Sender email (uses default if not provided)
            cc_emails: CC recipients
            bcc_emails: BCC recipients
            attachments: List of file paths to attach

        Returns:
            Send result
        """
        try:
            self.logger.info("Sending email", to=to_emails, subject=subject)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or settings.email.from_email
            msg['To'] = ', '.join(to_emails)

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # TODO: Add attachment support
            if attachments:
                self.logger.warning("Attachments not yet implemented")

            # Send email
            with smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port) as server:
                if settings.email.smtp_use_tls:
                    server.starttls()

                if settings.email.smtp_username and settings.email.smtp_password:
                    server.login(settings.email.smtp_username, settings.email.smtp_password)

                recipients = to_emails + (cc_emails or []) + (bcc_emails or [])
                server.send_message(msg, to_addrs=recipients)

            self.logger.info("Email sent successfully", to=to_emails)

            return ToolResult(
                success=True,
                data={
                    'sent_to': to_emails,
                    'subject': subject,
                    'message': 'Email sent successfully',
                },
                metadata={'recipients_count': len(to_emails)},
            )

        except Exception as e:
            self.logger.error("Email sending failed", error=str(e))
            return ToolResult(
                success=False,
                error=f"Email sending failed: {str(e)}",
            )





