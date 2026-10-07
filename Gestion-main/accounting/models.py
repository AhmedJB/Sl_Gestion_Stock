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
    Official accounting invoice for purchases (ACHAT), sales (VENTE)
    or credit notes (AVOIR, goods returned / refund to client).

    invoice_number is sequential per year and type:
      FA-2026-00001 for purchases
      FV-2026-00001 for sales
      AV-2026-00001 for credit notes
    """
    INVOICE_TYPE_CHOICES = [
        ('ACHAT', 'Achat (Purchase)'),
        ('VENTE', 'Vente (Sale)'),
        ('AVOIR', 'Avoir (Credit Note)'),
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
    custom_reference = models.CharField(max_length=100, default='', blank=True, db_index=True, verbose_name='Custom Reference / Printed Number', help_text='Optional custom reference printed on the invoice instead of the system number.')
    invoice_type = models.CharField(max_length=5, choices=INVOICE_TYPE_CHOICES)
    
    # One of these will be set depending on invoice_type
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_invoices')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_invoices')
    
    total = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    payment_mode = models.CharField(max_length=50, default='', blank=True)  # CASH, CHECK, TRANSFER, etc.
    notes = models.TextField(default='', blank=True)
    invoice_date = models.DateTimeField(default=timezone.now, null=True, blank=True, db_index=True, verbose_name='Invoice Date', help_text='Editable accounting date printed on the invoice. Defaults to creation time.')

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

    @property
    def display_number(self):
        return self.custom_reference if self.custom_reference else self.invoice_number

    @property
    def effective_date(self):
        return self.invoice_date or self.created_at

    def generate_invoice_number(self):
        """
        Generates the next sequential invoice number for this
        fiscal year and type.
        """
        prefix = {'ACHAT': 'FA', 'VENTE': 'FV', 'AVOIR': 'AV'}.get(self.invoice_type, 'FV')
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
        if not self.invoice_date:
            self.invoice_date = timezone.now()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    A line item on an accounting invoice.

    Pricing (comptabilité, TTC-based since 10/2026):
    - unit_price = HT unit price (legacy field, kept for history)
    - unit_price_ttc = TTC unit price entered on the invoice (null on legacy rows)
    - total = TTC line total (qty * TTC) on new rows, HT total on legacy rows
    Effective values are exposed via properties so old invoices still print.
    """
    invoice = models.ForeignKey(AccountingInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    reference = models.CharField(max_length=100, default='', blank=True, db_index=True, verbose_name='Product Reference', help_text='Supplier catalogue reference printed on the invoice.')
    product_name = models.CharField(max_length=255)  # Denormalized for historical accuracy
    quantity = models.IntegerField(default=0)
    unit_price = models.FloatField(default=0)  # HT (legacy canonical)
    unit_price_ttc = models.FloatField(default=0)  # TTC entered (0/null = legacy row, derive x1.2)
    discount = models.FloatField(default=0, verbose_name='Remise (%)', help_text='Line discount percent, e.g. 35 = -35%. Applied on the TTC line total.')
    total = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        ref = f"[{self.reference}] " if self.reference else ""
        return f"{ref}{self.product_name} x{self.quantity}"

    @property
    def discount_factor(self):
        try:
            d = float(self.discount or 0)
        except (TypeError, ValueError):
            d = 0
        return max(0.0, min(1.0, 1.0 - d / 100.0))

    @property
    def effective_unit_ttc(self):
        if self.unit_price_ttc:
            return self.unit_price_ttc
        return round(self.unit_price * 1.2, 2)

    @property
    def effective_unit_ht(self):
        if self.unit_price_ttc:
            return round(self.unit_price_ttc / 1.2, 2)
        return self.unit_price

    @property
    def effective_total_ttc(self):
        if self.unit_price_ttc:
            return round(self.quantity * self.unit_price_ttc * self.discount_factor, 2)
        return round(self.quantity * self.unit_price * 1.2 * self.discount_factor, 2)

    def save(self, *args, **kwargs):
        if self.unit_price_ttc:
            if not self.unit_price:
                self.unit_price = round(self.unit_price_ttc / 1.2, 2)
            self.total = round(self.quantity * self.unit_price_ttc * self.discount_factor, 2)
        else:
            self.total = round(self.quantity * self.unit_price * self.discount_factor, 2)
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
