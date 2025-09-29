#!/usr/bin/env python3
"""Example email processing workflow using AI automation agents."""

import asyncio
import json
from typing import Dict, List

from src.agents.task import TaskAgent, TaskConfig, TaskStep
from src.agents.decision import DecisionAgent, DecisionConfig
from src.config import get_settings
from src.logging import get_logger, setup_logging
from src.monitoring import init_monitoring, track_performance

# Setup logging and monitoring
setup_logging()
init_monitoring()
logger = get_logger(__name__)
settings = get_settings()


class EmailProcessor(TaskAgent):
    """Agent for processing incoming emails."""

    def __init__(self):
        """Initialize the email processor."""
        config = TaskConfig(
            name="email_processor",
            description="Processes incoming emails and categorizes them",
            task_type="email_processing",
            required_tools=["email_reader", "categorizer", "responder"],
            required_input_fields=["email_id", "email_content", "sender"]
        )
        super().__init__(config)

    async def _get_task_steps(self, input_data: Dict) -> List[TaskStep]:
        """Define the steps for email processing."""
        return [
            TaskStep(
                name="read_email",
                description="Read and parse the email content",
                tool="email_reader",
                parameters={"email_id": input_data["email_id"]}
            ),
            TaskStep(
                name="categorize_email",
                description="Categorize the email based on content and sender",
                tool="categorizer",
                parameters={
                    "content": input_data["email_content"],
                    "sender": input_data["sender"]
                }
            ),
            TaskStep(
                name="generate_response",
                description="Generate appropriate response based on category",
                tool="responder",
                parameters={
                    "category": "{{categorize_email.result.category}}",
                    "urgency": "{{categorize_email.result.urgency}}"
                }
            )
        ]


class EmailCategorizer:
    """Tool for categorizing emails."""

    async def execute(self, parameters: Dict, input_data: Dict) -> Dict:
        """Categorize an email."""
        content = parameters.get("content", "")
        sender = parameters.get("sender", "")

        # Simple categorization logic (in production, use ML models)
        categories = {
            "spam": ["free money", "congratulations", "winner", "urgent"],
            "support": ["help", "issue", "problem", "error"],
            "sales": ["interested", "demo", "pricing", "quote"],
            "partnership": ["collaboration", "partner", "alliance"]
        }

        category = "general"
        urgency = "low"

        # Check for spam keywords
        content_lower = content.lower()
        for cat, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                category = cat
                break

        # Determine urgency
        urgency_keywords = ["urgent", "asap", "emergency", "critical"]
        if any(keyword in content_lower for keyword in urgency_keywords):
            urgency = "high"

        return {
            "success": True,
            "category": category,
            "urgency": urgency,
            "confidence": 0.85
        }


class EmailResponder:
    """Tool for generating email responses."""

    async def execute(self, parameters: Dict, input_data: Dict) -> Dict:
        """Generate a response for the email."""
        category = parameters.get("category", "general")
        urgency = parameters.get("urgency", "low")

        responses = {
            "spam": "Thank you for your email. We have received your message.",
            "support": "Thank you for contacting our support team. We will review your issue and respond within 24 hours.",
            "sales": "Thank you for your interest! Our sales team will contact you shortly to discuss your needs.",
            "partnership": "Thank you for your partnership inquiry. We will review your proposal and get back to you soon.",
            "general": "Thank you for your email. We have received your message and will respond appropriately."
        }

        response = responses.get(category, responses["general"])

        if urgency == "high":
            response = f"URGENT: {response}"

        return {
            "success": True,
            "response": response,
            "category": category,
            "requires_human_review": category in ["partnership", "sales"]
        }


async def main():
    """Main function to demonstrate the email processing workflow."""
    logger.info("Starting email processing workflow example")

    # Create agents
    email_processor = EmailProcessor()

    # Register tools
    email_processor.register_tool("email_reader", EmailCategorizer())
    email_processor.register_tool("categorizer", EmailCategorizer())
    email_processor.register_tool("responder", EmailResponder())

    # Example email data
    test_emails = [
        {
            "email_id": "001",
            "email_content": "I need help with my account. There's an error when I try to log in.",
            "sender": "user@example.com"
        },
        {
            "email_id": "002",
            "email_content": "Congratulations! You have won $1,000,000! Click here to claim your prize.",
            "sender": "scam@fake-site.com"
        },
        {
            "email_id": "003",
            "email_content": "We are interested in exploring a partnership opportunity with your company.",
            "sender": "business@partner.com"
        }
    ]

    # Process each email
    for email in test_emails:
        logger.info(f"Processing email {email['email_id']}")

        try:
            result = await email_processor.execute_with_retry(email)

            if result.success:
                logger.info(
                    "Email processed successfully",
                    email_id=email["email_id"],
                    category=result.data.get("category"),
                    response=result.data.get("response")
                )
            else:
                logger.error(
                    "Email processing failed",
                    email_id=email["email_id"],
                    error=result.error
                )

        except Exception as e:
            logger.error(
                "Unexpected error processing email",
                email_id=email["email_id"],
                error=str(e)
            )

    logger.info("Email processing workflow completed")


if __name__ == "__main__":
    asyncio.run(main())
