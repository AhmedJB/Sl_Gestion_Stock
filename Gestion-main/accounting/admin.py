from django.contrib import admin
from .models import FiscalYear, StockSnapshot, AccountingInvoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ('total',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_locked', 'opened_at', 'closed_at')
    list_filter = ('is_locked',)


@admin.register(StockSnapshot)
class StockSnapshotAdmin(admin.ModelAdmin):
    list_display = ('fiscal_year', 'product', 'initial_qty', 'current_qty')
    list_filter = ('fiscal_year',)
    search_fields = ('product__name', 'product__p_id')


@admin.register(AccountingInvoice)
class AccountingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_type', 'fiscal_year',
                    'provider', 'client', 'total', 'status', 'created_at')
    list_filter = ('invoice_type', 'status', 'fiscal_year')
    search_fields = ('invoice_number',)
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product_name', 'quantity', 'unit_price', 'total')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_mode', 'reference', 'paid_at')
    list_filter = ('payment_mode',)
