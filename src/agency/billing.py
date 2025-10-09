"""Billing and invoicing for AI automation agency."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class InvoiceStatus(str, Enum):
    """Invoice status."""

    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class InvoiceLineItem(BaseModel):
    """Invoice line item."""

    description: str
    quantity: float
    unit_price: float
    amount: float
    metadata: Dict = {}


class Invoice(BaseModel):
    """Invoice model."""

    id: str
    client_id: str
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: datetime
    due_date: datetime
    items: List[InvoiceLineItem] = []
    subtotal: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    notes: Optional[str] = None
    metadata: Dict = {}
    created_at: datetime = datetime.utcnow()
    paid_at: Optional[datetime] = None


class Subscription(BaseModel):
    """Subscription model."""

    id: str
    client_id: str
    plan_name: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    monthly_price: float
    billing_cycle: str = "monthly"  # monthly, quarterly, annual
    start_date: datetime
    end_date: Optional[datetime] = None
    next_billing_date: datetime
    auto_renew: bool = True
    included_features: List[str] = []
    usage_limits: Dict = {}
    metadata: Dict = {}
    created_at: datetime = datetime.utcnow()


class BillingManager:
    """Manager for billing operations."""

    def __init__(self):
        """Initialize billing manager."""
        self.logger = logger.bind(component="billing_manager")

    async def create_invoice(
        self,
        client_id: str,
        items: List[Dict],
        due_days: int = 30,
        tax_rate: float = 0.0,
        notes: str = None,
    ) -> Invoice:
        """Create a new invoice.

        Args:
            client_id: Client ID
            items: Invoice line items
            due_days: Days until due
            tax_rate: Tax rate (as decimal, e.g., 0.1 for 10%)
            notes: Additional notes

        Returns:
            Created invoice
        """
        self.logger.info("Creating invoice", client_id=client_id)

        # Convert items to line items
        line_items = []
        subtotal = 0.0

        for item in items:
            amount = item["quantity"] * item["unit_price"]
            line_items.append(
                InvoiceLineItem(
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    amount=amount,
                    metadata=item.get("metadata", {}),
                )
            )
            subtotal += amount

        # Calculate tax and total
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        issue_date = datetime.utcnow()
        due_date = issue_date + timedelta(days=due_days)

        invoice = Invoice(
            id=self._generate_invoice_id(),
            client_id=client_id,
            invoice_number=self._generate_invoice_number(),
            issue_date=issue_date,
            due_date=due_date,
            items=line_items,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total,
            notes=notes,
        )

        self.logger.info("Invoice created", invoice_id=invoice.id, total=total)
        return invoice

    async def mark_invoice_paid(self, invoice_id: str) -> bool:
        """Mark an invoice as paid.

        Args:
            invoice_id: Invoice ID

        Returns:
            True if updated
        """
        self.logger.info("Marking invoice as paid", invoice_id=invoice_id)
        # TODO: Update in database
        return True

    async def create_subscription(
        self,
        client_id: str,
        plan_name: str,
        monthly_price: float,
        billing_cycle: str = "monthly",
        included_features: List[str] = None,
        usage_limits: Dict = None,
    ) -> Subscription:
        """Create a subscription.

        Args:
            client_id: Client ID
            plan_name: Subscription plan name
            monthly_price: Monthly price
            billing_cycle: Billing cycle
            included_features: Included features
            usage_limits: Usage limits

        Returns:
            Created subscription
        """
        self.logger.info("Creating subscription", client_id=client_id, plan=plan_name)

        start_date = datetime.utcnow()
        next_billing_date = self._calculate_next_billing_date(start_date, billing_cycle)

        subscription = Subscription(
            id=self._generate_subscription_id(),
            client_id=client_id,
            plan_name=plan_name,
            monthly_price=monthly_price,
            billing_cycle=billing_cycle,
            start_date=start_date,
            next_billing_date=next_billing_date,
            included_features=included_features or [],
            usage_limits=usage_limits or {},
        )

        self.logger.info("Subscription created", subscription_id=subscription.id)
        return subscription

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription.

        Args:
            subscription_id: Subscription ID

        Returns:
            True if cancelled
        """
        self.logger.info("Cancelling subscription", subscription_id=subscription_id)
        # TODO: Update in database
        return True

    async def generate_recurring_invoices(self) -> List[Invoice]:
        """Generate recurring invoices for active subscriptions.

        Returns:
            List of generated invoices
        """
        self.logger.info("Generating recurring invoices")
        # TODO: Query subscriptions due for billing
        # Create invoices for each
        return []

    def _generate_invoice_id(self) -> str:
        """Generate unique invoice ID."""
        import uuid
        return f"inv_{uuid.uuid4().hex[:12]}"

    def _generate_invoice_number(self) -> str:
        """Generate invoice number."""
        # Format: INV-YYYY-MM-XXXXX
        now = datetime.utcnow()
        import random
        seq = random.randint(10000, 99999)
        return f"INV-{now.year}-{now.month:02d}-{seq}"

    def _generate_subscription_id(self) -> str:
        """Generate unique subscription ID."""
        import uuid
        return f"sub_{uuid.uuid4().hex[:12]}"

    def _calculate_next_billing_date(
        self,
        start_date: datetime,
        billing_cycle: str,
    ) -> datetime:
        """Calculate next billing date.

        Args:
            start_date: Subscription start date
            billing_cycle: Billing cycle

        Returns:
            Next billing date
        """
        if billing_cycle == "monthly":
            return start_date + timedelta(days=30)
        elif billing_cycle == "quarterly":
            return start_date + timedelta(days=90)
        elif billing_cycle == "annual":
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)





