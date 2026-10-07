from rest_framework import serializers
from .models import FiscalYear, StockSnapshot, AccountingInvoice, InvoiceItem, Payment
from controller.serializer import ProviderSerializer, ClientSerializer, ProductSerializer


class FiscalYearSerializer(serializers.ModelSerializer):
    invoice_count = serializers.SerializerMethodField()
    snapshot_count = serializers.SerializerMethodField()

    class Meta:
        model = FiscalYear
        fields = ['id', 'year', 'is_locked', 'opened_at', 'closed_at', 'notes',
                  'invoice_count', 'snapshot_count']

    def get_invoice_count(self, obj):
        return obj.invoices.count()

    def get_snapshot_count(self, obj):
        return obj.snapshots.count()


class StockSnapshotSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_p_id = serializers.CharField(source='product.p_id', read_only=True)
    product_reference = serializers.CharField(source='product.reference', read_only=True, default='')

    class Meta:
        model = StockSnapshot
        fields = ['id', 'fiscal_year', 'product', 'product_detail',
                  'product_name', 'product_p_id', 'product_reference',
                  'initial_qty', 'current_qty']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'payment_mode', 'reference',
                  'paid_at', 'notes']
        extra_kwargs = {'invoice': {'required': False}}


class InvoiceItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    effective_unit_ttc = serializers.FloatField(read_only=True)
    effective_unit_ht = serializers.FloatField(read_only=True)
    effective_total_ttc = serializers.FloatField(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'invoice', 'product', 'product_detail',
                  'reference', 'product_name', 'quantity',
                  'unit_price', 'unit_price_ttc', 'discount',
                  'effective_unit_ht', 'effective_unit_ttc', 'effective_total_ttc',
                  'total']
        extra_kwargs = {
            'invoice': {'required': False},
            'total': {'read_only': True},
        }


class AccountingInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    provider_detail = ProviderSerializer(source='provider', read_only=True)
    client_detail = ClientSerializer(source='client', read_only=True)
    total_paid = serializers.FloatField(read_only=True)
    balance_due = serializers.FloatField(read_only=True)
    display_number = serializers.CharField(read_only=True)
    effective_date = serializers.DateTimeField(read_only=True)
    fiscal_year_display = serializers.IntegerField(source='fiscal_year.year', read_only=True)

    class Meta:
        model = AccountingInvoice
        fields = ['id', 'fiscal_year', 'fiscal_year_display',
                  'invoice_number', 'custom_reference', 'display_number', 'invoice_type',
                  'provider', 'provider_detail',
                  'client', 'client_detail',
                  'total', 'status', 'payment_mode', 'notes',
                  'invoice_date', 'effective_date',
                  'total_paid', 'balance_due',
                  'items', 'payments',
                  'created_at', 'updated_at']
        extra_kwargs = {
            'invoice_number': {'required': False, 'read_only': True},
            'custom_reference': {'required': False, 'allow_blank': True},
            'invoice_date': {'required': False},
            'total': {'required': False},
        }


class AccountingInvoiceListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views (no nested items/payments)."""
    provider_name = serializers.CharField(source='provider.name', read_only=True, default='')
    client_name = serializers.CharField(source='client.name', read_only=True, default='')
    total_paid = serializers.FloatField(read_only=True)
    balance_due = serializers.FloatField(read_only=True)
    display_number = serializers.CharField(read_only=True)
    effective_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AccountingInvoice
        fields = ['id', 'fiscal_year', 'invoice_number', 'custom_reference', 'display_number', 'invoice_type',
                  'provider', 'provider_name',
                  'client', 'client_name',
                  'total', 'total_paid', 'balance_due',
                  'status', 'payment_mode',
                  'invoice_date', 'effective_date',
                  'created_at']


class CreateInvoiceSerializer(serializers.Serializer):
    """
    Serializer for creating an invoice with its items in a single request.
    """
    fiscal_year_id = serializers.IntegerField()
    invoice_type = serializers.ChoiceField(choices=['ACHAT', 'VENTE', 'AVOIR'])
    provider_id = serializers.IntegerField(required=False, allow_null=True)
    client_id = serializers.IntegerField(required=False, allow_null=True)
    payment_mode = serializers.CharField(required=False, default='', allow_blank=True)
    notes = serializers.CharField(required=False, default='', allow_blank=True)
    custom_reference = serializers.CharField(required=False, default='', allow_blank=True)
    invoice_date = serializers.DateTimeField(required=False)
    items = serializers.ListField(child=serializers.DictField(), min_length=1)
    # Each item dict: { product_id: int, reference: str, product_name: str, quantity: int, unit_price_ttc: float (or legacy unit_price), discount: float (remise %) }

    def validate(self, data):
        if data['invoice_type'] == 'ACHAT' and not data.get('provider_id'):
            raise serializers.ValidationError("provider_id is required for purchase invoices.")
        if data['invoice_type'] == 'VENTE' and not data.get('client_id'):
            raise serializers.ValidationError("client_id is required for sale invoices.")
        if data['invoice_type'] == 'AVOIR' and not data.get('client_id'):
            raise serializers.ValidationError("client_id is required for credit notes (avoir).")
        return data
