from django.db import models
from django.utils import timezone
from controller.models import Product, Provider, Client


class FiscalYear(models.Model):
    """
    Represents a fiscal/accounting year.
    When a year is 'locked', no further invoice or stock changes
    can be made within it.
    """
    year = models.IntegerField(unique=True, db_index=True)
    is_locked = models.BooleanField(default=False)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(default='', blank=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'Fiscal Year'
        verbose_name_plural = 'Fiscal Years'

    def __str__(self):
        status = 'Locked' if self.is_locked else 'Active'
        return f"FY-{self.year} ({status})"


class StockSnapshot(models.Model):
    """
    Records the stock level of a product at the start of a fiscal year
    and tracks the current quantity as invoices modify it.
    
    initial_qty = quantity imported when the year was initialized
    current_qty = initial_qty + purchases - sales within this year
    """
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='snapshots')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_snapshots')
    initial_qty = models.IntegerField(default=0)
    current_qty = models.IntegerField(default=0)

    class Meta:
        unique_together = ('fiscal_year', 'product')
        ordering = ['product__name']
        verbose_name = 'Stock Snapshot'
        verbose_name_plural = 'Stock Snapshots'

    def __str__(self):
        return f"{self.product.name} @ FY-{self.fiscal_year.year}: {self.current_qty}"


class AccountingInvoice(models.Model):
    """
    Official accounting invoice for purchases (ACHAT) or sales (VENTE).
    
    invoice_number is sequential per year and type:
      FA-2026-00001 for purchases
      FV-2026-00001 for sales
    """
    INVOICE_TYPE_CHOICES = [
        ('ACHAT', 'Achat (Purchase)'),
        ('VENTE', 'Vente (Sale)'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('PAID', 'Fully Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=20, unique=True, db_index=True)
    invoice_type = models.CharField(max_length=5, choices=INVOICE_TYPE_CHOICES)
    
    # One of these will be set depending on invoice_type
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_invoices')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_invoices')
    
    total = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    payment_mode = models.CharField(max_length=50, default='', blank=True)  # CASH, CHECK, TRANSFER, etc.
    notes = models.TextField(default='', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Accounting Invoice'
        verbose_name_plural = 'Accounting Invoices'

    def __str__(self):
        return self.invoice_number

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def balance_due(self):
        return self.total - self.total_paid

    def generate_invoice_number(self):
        """
        Generates the next sequential invoice number for this
        fiscal year and type.
        """
        prefix = 'FA' if self.invoice_type == 'ACHAT' else 'FV'
        year = self.fiscal_year.year

        last = AccountingInvoice.objects.filter(
            fiscal_year=self.fiscal_year,
            invoice_type=self.invoice_type,
        ).order_by('-invoice_number').first()

        if last:
            # Extract the sequence number from e.g. "FA-2026-00042"
            try:
                seq = int(last.invoice_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"{prefix}-{year}-{str(seq).zfill(5)}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    A line item on an accounting invoice.
    """
    invoice = models.ForeignKey(AccountingInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    product_name = models.CharField(max_length=255)  # Denormalized for historical accuracy
    quantity = models.IntegerField(default=0)
    unit_price = models.FloatField(default=0)
    total = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Records a payment made against an invoice. Supports partial
    payments over time, creating a full audit trail.
    """
    PAYMENT_MODE_CHOICES = [
        ('CASH', 'Espèces'),
        ('CHECK', 'Chèque'),
        ('TRANSFER', 'Virement'),
        ('OTHER', 'Autre'),
    ]

    invoice = models.ForeignKey(AccountingInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField(default=0)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, default='CASH')
    reference = models.CharField(max_length=255, default='', blank=True)  # Check number, transfer ref, etc.
    paid_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(default='', blank=True)

    class Meta:
        ordering = ['-paid_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment {self.amount} on {self.invoice.invoice_number}"
