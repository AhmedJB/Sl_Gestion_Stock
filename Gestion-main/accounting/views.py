from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone

from .models import FiscalYear, StockSnapshot, AccountingInvoice, InvoiceItem, Payment
from .serializers import (
    FiscalYearSerializer,
    StockSnapshotSerializer,
    AccountingInvoiceSerializer,
    AccountingInvoiceListSerializer,
    CreateInvoiceSerializer,
    InvoiceItemSerializer,
    PaymentSerializer,
)
from .permissions import IsAccountingUser
from controller.models import Product, Provider, Client


# ──────────────────────────────────────────────
#  Fiscal Year Management
# ──────────────────────────────────────────────

class FiscalYearViewSet(ModelViewSet):
    """
    CRUD for fiscal years, plus custom actions to
    initialize stock and close/lock a year.
    """
    permission_classes = [IsAccountingUser]
    serializer_class = FiscalYearSerializer
    queryset = FiscalYear.objects.all()

    @action(detail=True, methods=['post'])
    def initialize(self, request, pk=None):
        """
        Manually initialize stock for specific products for this fiscal year.
        Expects payload:
        {
            "items": [
                {"product_id": 1, "quantity": 50},
                {"product_id": 2, "quantity": 100}
            ]
        }
        """
        fy = self.get_object()
        if fy.is_locked:
            return Response(
                {'error': 'This fiscal year is locked.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        items = request.data.get('items', [])
        if not items:
            return Response(
                {'error': 'No items provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_ids = [item.get('product_id') for item in items if item.get('product_id')]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        snapshots = []
        with transaction.atomic():
            for item in items:
                pid = item.get('product_id')
                qty = int(item.get('quantity', 0))
                
                if pid in product_map:
                    # Update or create the snapshot
                    snapshot, created = StockSnapshot.objects.get_or_create(
                        fiscal_year=fy,
                        product=product_map[pid],
                        defaults={'initial_qty': qty, 'current_qty': qty}
                    )
                    if not created:
                        snapshot.initial_qty = qty
                        snapshot.current_qty = qty
                        snapshot.save()
                    snapshots.append(snapshot)

        return Response({
            'message': f'Successfully initialized {len(snapshots)} products for FY-{fy.year}.',
            'count': len(snapshots),
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Lock the fiscal year and optionally create the
        next year with carried-over stock.
        """
        fy = self.get_object()
        if fy.is_locked:
            return Response(
                {'error': 'Already locked.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        create_next = request.data.get('create_next_year', False)

        with transaction.atomic():
            fy.is_locked = True
            fy.closed_at = timezone.now()
            fy.save()

            result = {'message': f'FY-{fy.year} has been locked.'}

            if create_next:
                next_year_val = fy.year + 1
                next_fy, created = FiscalYear.objects.get_or_create(year=next_year_val)
                current_snapshots = fy.snapshots.all()
                carried = 0
                for snap in current_snapshots:
                    StockSnapshot.objects.update_or_create(
                        fiscal_year=next_fy,
                        product=snap.product,
                        defaults={
                            'initial_qty': snap.current_qty,
                            'current_qty': snap.current_qty,
                        }
                    )
                    carried += 1
                result['next_year'] = FiscalYearSerializer(next_fy).data
                if created:
                    result['message'] += f' FY-{next_year_val} created with {carried} carried-over snapshots.'
                else:
                    result['message'] += f' FY-{next_year_val} updated with {carried} carried-over snapshots.'

        return Response(result, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
#  Stock Snapshot (read-only for the most part)
# ──────────────────────────────────────────────

class StockSnapshotViewSet(ModelViewSet):
    """
    View and manage stock snapshots for a given fiscal year.
    Filterable via ?year=2026
    """
    permission_classes = [IsAccountingUser]
    serializer_class = StockSnapshotSerializer

    def get_queryset(self):
        qs = StockSnapshot.objects.select_related('product', 'fiscal_year').all()
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(fiscal_year__year=int(year))
        return qs


# ──────────────────────────────────────────────
#  Invoice Management
# ──────────────────────────────────────────────

class AccountingInvoiceViewSet(ModelViewSet):
    """
    List / retrieve / create invoices.
    
    For creation, use the CreateInvoiceSerializer format
    which accepts items inline.
    
    Filterable via ?year=2026&type=ACHAT&status=PAID
    """
    permission_classes = [IsAccountingUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountingInvoiceListSerializer
        if self.action == 'create':
            return CreateInvoiceSerializer
        return AccountingInvoiceSerializer

    def get_queryset(self):
        qs = AccountingInvoice.objects.select_related(
            'fiscal_year', 'provider', 'client'
        ).prefetch_related('items', 'payments').all()

        year = self.request.query_params.get('year')
        inv_type = self.request.query_params.get('type')
        inv_status = self.request.query_params.get('status')
        provider_id = self.request.query_params.get('provider_id')
        client_id = self.request.query_params.get('client_id')

        if year:
            qs = qs.filter(fiscal_year__year=int(year))
        if inv_type:
            qs = qs.filter(invoice_type=inv_type.upper())
        if inv_status:
            qs = qs.filter(status=inv_status.upper())
        if provider_id:
            qs = qs.filter(provider_id=int(provider_id))
        if client_id:
            qs = qs.filter(client_id=int(client_id))

        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = CreateInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            fy = FiscalYear.objects.get(id=data['fiscal_year_id'])
        except FiscalYear.DoesNotExist:
            return Response(
                {'error': 'Fiscal year not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if fy.is_locked:
            return Response(
                {'error': 'This fiscal year is locked. No new invoices allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the invoice
        invoice = AccountingInvoice(
            fiscal_year=fy,
            invoice_type=data['invoice_type'],
            provider_id=data.get('provider_id'),
            client_id=data.get('client_id'),
            payment_mode=data.get('payment_mode', ''),
            notes=data.get('notes', ''),
            status='CONFIRMED',
        )
        invoice.save()  # triggers generate_invoice_number

        # Create line items and update stock snapshots
        total = 0
        for item_data in data['items']:
            product_id = item_data.get('product_id')
            quantity = int(item_data.get('quantity', 0))
            unit_price = float(item_data.get('unit_price', 0))

            product = None
            product_name = item_data.get('product_name', '')
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    product_name = product.name
                except Product.DoesNotExist:
                    pass

            item = InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
            )
            total += item.total

            # Update the stock snapshot for this year
            if product:
                snapshot, _ = StockSnapshot.objects.get_or_create(
                    fiscal_year=fy,
                    product=product,
                    defaults={'initial_qty': product.quantity, 'current_qty': product.quantity}
                )
                if data['invoice_type'] == 'ACHAT':
                    snapshot.current_qty += quantity
                elif data['invoice_type'] == 'VENTE':
                    snapshot.current_qty -= quantity
                snapshot.save()

        invoice.total = total
        invoice.save()

        return Response(
            AccountingInvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an invoice and reverse stock changes."""
        invoice = self.get_object()
        if invoice.status == 'CANCELLED':
            return Response({'error': 'Already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        fy = invoice.fiscal_year
        if fy.is_locked:
            return Response({'error': 'Fiscal year is locked.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Reverse stock snapshot changes
            for item in invoice.items.all():
                if item.product:
                    try:
                        snapshot = StockSnapshot.objects.get(
                            fiscal_year=fy, product=item.product
                        )
                        if invoice.invoice_type == 'ACHAT':
                            snapshot.current_qty -= item.quantity
                        elif invoice.invoice_type == 'VENTE':
                            snapshot.current_qty += item.quantity
                        snapshot.save()
                    except StockSnapshot.DoesNotExist:
                        pass

            invoice.status = 'CANCELLED'
            invoice.save()

        return Response(AccountingInvoiceSerializer(invoice).data)


# ──────────────────────────────────────────────
#  Payment Management
# ──────────────────────────────────────────────

class PaymentViewSet(ModelViewSet):
    """
    Record payments against invoices.
    Filterable via ?invoice_id=123
    """
    permission_classes = [IsAccountingUser]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = Payment.objects.select_related('invoice').all()
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            qs = qs.filter(invoice_id=int(invoice_id))
        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            invoice = AccountingInvoice.objects.get(id=data.get('invoice_id'))
        except AccountingInvoice.DoesNotExist:
            return Response({'error': 'Invoice not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if invoice.fiscal_year.is_locked:
            return Response({'error': 'Fiscal year is locked.'}, status=status.HTTP_400_BAD_REQUEST)

        if invoice.status == 'CANCELLED':
            return Response({'error': 'Cannot pay a cancelled invoice.'}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            invoice=invoice,
            amount=float(data.get('amount', 0)),
            payment_mode=data.get('payment_mode', 'CASH'),
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
        )

        # Update invoice status
        if invoice.balance_due <= 0:
            invoice.status = 'PAID'
        else:
            invoice.status = 'PARTIAL'
        invoice.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────
#  Accounting Statistics
# ──────────────────────────────────────────────

class AccountingStatsView(APIView):
    """
    Returns accounting statistics for a given fiscal year.
    
    GET /api/accounting/stats/?year=2026
    
    Returns:
    - valeur_marchandise: total value of current stock (qty * price_achat)
    - valeur_vendue: total value of confirmed sales
    - total_achats: total value of confirmed purchases
    - profit: sales - purchase cost of sold items
    - debts_providers: outstanding balance owed to providers (unpaid purchase invoices)
    - debts_clients: outstanding balance owed by clients (unpaid sale invoices)
    - top_products_sold: top 5 products by quantity sold
    - invoice_counts: { achat, vente, total }
    """
    permission_classes = [IsAccountingUser]

    def get(self, request):
        year = request.query_params.get('year')
        if not year:
            return Response({'error': 'year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fy = FiscalYear.objects.get(year=int(year))
        except FiscalYear.DoesNotExist:
            return Response({'error': f'Fiscal year {year} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Stock value from snapshots
        stock_value = StockSnapshot.objects.filter(fiscal_year=fy).aggregate(
            total=Sum(F('current_qty') * F('product__price_achat'))
        )['total'] or 0

        # Active invoices (not cancelled)
        active_invoices = AccountingInvoice.objects.filter(
            fiscal_year=fy
        ).exclude(status='CANCELLED')

        # Sales total
        sales_total = active_invoices.filter(
            invoice_type='VENTE'
        ).aggregate(total=Sum('total'))['total'] or 0

        # Purchase total
        purchase_total = active_invoices.filter(
            invoice_type='ACHAT'
        ).aggregate(total=Sum('total'))['total'] or 0

        # Profit = sales revenue - cost of goods sold
        cogs = InvoiceItem.objects.filter(
            invoice__fiscal_year=fy,
            invoice__invoice_type='VENTE',
        ).exclude(
            invoice__status='CANCELLED'
        ).aggregate(
            total=Sum(F('quantity') * F('product__price_achat'))
        )['total'] or 0

        profit = sales_total - cogs

        # Debts to providers (unpaid purchase invoices)
        purchase_invoices = active_invoices.filter(invoice_type='ACHAT')
        debts_providers = []
        for inv in purchase_invoices:
            balance = inv.balance_due
            if balance > 0:
                debts_providers.append({
                    'invoice_number': inv.invoice_number,
                    'provider': inv.provider.name if inv.provider else 'N/A',
                    'provider_id': inv.provider_id,
                    'total': inv.total,
                    'paid': inv.total_paid,
                    'balance': balance,
                })

        # Debts from clients (unpaid sale invoices)
        sale_invoices = active_invoices.filter(invoice_type='VENTE')
        debts_clients = []
        for inv in sale_invoices:
            balance = inv.balance_due
            if balance > 0:
                debts_clients.append({
                    'invoice_number': inv.invoice_number,
                    'client': inv.client.name if inv.client else 'N/A',
                    'client_id': inv.client_id,
                    'total': inv.total,
                    'paid': inv.total_paid,
                    'balance': balance,
                })

        # Top 5 products sold
        top_sold = InvoiceItem.objects.filter(
            invoice__fiscal_year=fy,
            invoice__invoice_type='VENTE',
        ).exclude(
            invoice__status='CANCELLED'
        ).values('product_name').annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum('total'),
        ).order_by('-total_qty')[:5]

        # Invoice counts
        achat_count = active_invoices.filter(invoice_type='ACHAT').count()
        vente_count = active_invoices.filter(invoice_type='VENTE').count()

        return Response({
            'fiscal_year': fy.year,
            'is_locked': fy.is_locked,
            'valeur_marchandise': round(stock_value, 2),
            'valeur_vendue': round(sales_total, 2),
            'total_achats': round(purchase_total, 2),
            'profit': round(profit, 2),
            'debts_providers': debts_providers,
            'debts_providers_total': round(sum(d['balance'] for d in debts_providers), 2),
            'debts_clients': debts_clients,
            'debts_clients_total': round(sum(d['balance'] for d in debts_clients), 2),
            'top_products_sold': list(top_sold),
            'invoice_counts': {
                'achat': achat_count,
                'vente': vente_count,
                'total': achat_count + vente_count,
            }
        })
