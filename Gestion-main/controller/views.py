from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status,permissions
from .serializer import ClientSerializer, InvoiceSerializer, OrderDetailsSerializer, OrderSerializer, RegisterSerializer,ProviderSerializer,ProductSerializer,OptionsSerializer,EcheanceSerializer, MvtStockSerializer, OptionCategoriesSerializer,ProductImageSerializer,GeneralOrderDetailsSerializer,TransportOptionsSerializer,ProductWithImageSerializer,ProductWithChangeSerialize
from .models import *
from gestionStock.settings import MEDIA_ROOT
from django.core.files import File
from .helper import format_fact, format_number
from br_handler import Generator
import random
import datetime as d
from datetime import datetime, date ,timedelta
from urllib.parse import unquote
from dateutil.relativedelta  import relativedelta
from collections import defaultdict
from django.utils  import timezone
from django.db.models import Sum

# Create your views here.

class Register(APIView):
    

    def post(self,request,format=None):
        data = request.data 
        print(data)
        s = RegisterSerializer(data=data)
        if s.is_valid():
            print('valid')
            resp = s.save()
            print(resp)
            return Response(resp)
        else:
            print('not valid')
            return Response({'result':'not created'})


class TestSession(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,format=None):
        user = request.user
        print(f'User is {user}')
        u = RegisterSerializer(user).data
        return Response(u)




class Download(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,id,format=None):
        user = request.user
        task = Invoices.objects.filter(f_id=id)
        if len(task) != 0:
            task = task[0]
            path = MEDIA_ROOT + '/' + task.path
            f = open(path, 'rb')
            pdfFile = File(f)
            response = HttpResponse(pdfFile.read())
            response['Content-Disposition'] = 'attachment;'
            return response
        else:
            return Response({"result" : 'failed'},status.HTTP_400_BAD_REQUEST)


class postDownload(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        data = request.data 
        print('here')
        print(data)
        if len(data) > 0:
            g = Generator()
            g.genPdf(data)
            path = MEDIA_ROOT + '/br.pdf'
            f = open(path, 'rb')
            pdfFile = File(f)
            response = HttpResponse(pdfFile.read())
            response['Content-Disposition'] = 'attachment;'
            return response
        else:
            return Response({"result" : 'failed'},status.HTTP_400_BAD_REQUEST)



class AddProvider(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        data = request.data 
        s = ProviderSerializer(data = data)
        p = Provider(name = data['name'],email = data['email'],phone=data['phone'],address=data['address'])
        p.save()
        ps = ProviderSerializer(p).data
        return Response(ps)

    def get(self,request,format=None):
        ps = Provider.objects.all()
        s = ProviderSerializer(ps,many=True).data
        return Response(s,status.HTTP_200_OK)


class getProviderProducts(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        provider_id  = request.query_params.get('fid',None)
        if provider_id:
            prov = Provider.objects.filter(id=provider_id).first()
            if prov:
                produdcts = Product.objects.filter(provider = prov)
                data = ProductWithChangeSerialize(produdcts,many=True).data
                return Response(data,status=status.HTTP_200_OK)
                
            else:
                print("no prov")
                return Response([],status=status.HTTP_400_BAD_REQUEST)

        else:
            
            return Response([],status=status.HTTP_400_BAD_REQUEST)

class ModifyProvider(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,id,format="None"):
        p = Provider.objects.filter(id=id)
        if len(p) != 0:
            p = p[0]
            data = ProviderSerializer(p).data
            p.delete()
        else:
            data= {}
        
        return Response(data, status.HTTP_200_OK)

    def post(self,request,id,format="None"):
        data = request.data
        supplier = Provider.objects.filter(id=id)[0]
        supplier.name = data['name']
        supplier.email = data['email']
        supplier.phone = data['phone']
        supplier.address = data['address']
        c = float(data['credit']) - float(data['creditp'])
        if c < 0:
            c = 0
        supplier.credit = c
        supplier.save()
        s = ProviderSerializer(supplier).data
        return Response(s,status.HTTP_200_OK)

class AddClient(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        data = request.data 
        s = ClientSerializer(data = data)
        p = Client(name = data['name'],email = data['email'],phone=data['phone'],address=data['address'])
        p.save()
        ps = ClientSerializer(p).data
        return Response(ps)

    def get(self,request,format=None):
        ps = Client.objects.all()
        s = ClientSerializer(ps,many=True).data
        return Response(s,status.HTTP_200_OK)


class OpenClient(APIView):


    def get(self,request,format=None):
        ps = Client.objects.all()
        s = ClientSerializer(ps,many=True).data
        print("here")
        return Response(s,status.HTTP_200_OK)



class ModifyClient(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,id,format="None"):
        p = Client.objects.filter(id=id)
        if len(p) != 0:
            p = p[0]
            data = ClientSerializer(p).data
            p.delete()
        else:
            data= {}
        
        return Response(data, status.HTTP_200_OK)

    def post(self,request,id,format="None"):
        data = request.data
        client = Client.objects.filter(id=id)[0]
        client.name = data['name']
        client.email = data['email']
        client.phone = data['phone']
        client.address = data['address']
        client.credit = float(data['credit']) - float(data['creditp'])
        client.save()
        s = ClientSerializer(client).data
        return Response(s,status.HTTP_200_OK)






class AddProduct(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        data = request.data 
        print(data)
        supplier = Provider.objects.filter(id=data['fournisseur'])[0]
        if (supplier.credit + ((float(data['product']['quantity']) * float(data['product']['price_achat'])) - float(data['product']['paid'])) >= 0):
            supplier.credit += ((float(data['product']['quantity']) * float(data['product']['price_achat'])) - float(data['product']['paid']))
        
        if int(data['product']['quantity']) >= 0:
            product = supplier.product_set.create(name=data['product']['name'],ptype=data['product']['ptype'],price_vente=data['product']['price_vente'],price_achat=data['product']['price_achat'],paid=data['product']['paid'])
            product.quantity= int(data['product']['quantity'])
        else:
            return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)

        while True:
            idd = format_number(random.randrange(0,9999999999999))
            orders = Product.objects.filter(p_id=idd)
            if len(orders) == 0:
                break
        
        product.p_id = idd
        product.save()
        supplier.save()
        options = product.options_set.create(metal=data['options']['metal'],type=data['options']['type'])
        options.save()
        resp = {
            'fournisseur':ProviderSerializer(supplier).data,
            'product':ProductSerializer(product).data,
            'options' : OptionsSerializer(options).data
        }
        return Response(resp,status.HTTP_200_OK)

    
    def get(self,request,format=None):
        resps = []
        products = Product.objects.all().order_by('-quantity')
        for product  in products:
            supplier = product.provider
            options = product.options_set.all()[0]
            images = ProductImage.objects.filter(product=product)
            resp = {
            'fournisseur':ProviderSerializer(supplier).data,
            'product':ProductSerializer(product).data,
            'options' : OptionsSerializer(options).data,
            'images' : ProductImageSerializer(images,many=True).data
            }
            resps.append(resp)
        return Response(resps,status.HTTP_200_OK)
    
class SilentGetProducts(APIView):
    permission_classes = [permissions.AllowAny]


    def get(self,request,format=None):
        resps = []
        products = Product.objects.all().order_by('-quantity')
        for product  in products:
            supplier = product.provider
            options = product.options_set.all()[0]
            images = ProductImage.objects.filter(product=product)
            resp = {
            'fournisseur':ProviderSerializer(supplier).data,
            'product':ProductSerializer(product).data,
            'options' : OptionsSerializer(options).data,
            'images' : ProductImageSerializer(images,many=True).data
            }
            resps.append(resp)
        return Response(resps,status.HTTP_200_OK)

class SilentGetProductsInfo(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request,format="json"):
        data = request.data 
        ids = data.get("ids",[])
        print("received ids , " , ids)
        if len(ids) > 0:
            result = []
            for id_ in ids:
                p = Product.objects.filter(p_id=id_).first()
                if p:
                    result.append(ProductWithImageSerializer(p).data)

                else:
                    continue
            print("full result ", result)
            return Response(result,status.HTTP_200_OK)
        else:
            return Response([],status.HTTP_400_BAD_REQUEST)     
    
class SilentGetInfo(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request,format="json"):
        data = request.data
        print(data)
        
        if  data:
            products_obj= []
            for id_ in data:
                p= Product.objects.filter(p_id=id_).first()
                if p:
                    products_obj.append(p)
                
            return Response(ProductSerializer(products_obj,many=True).data,status.HTTP_200_OK)

        else:
            return Response([],status.HTTP_400_BAD_REQUEST)    

class ProductImageViewSet(ModelViewSet):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductImageSerializer
    
    def get_queryset(self):
        pid = self.request.GET.get("pid",False)
        if pid:
            product = Product.objects.filter(id = int(pid)).first()
            if product:
                return ProductImage.objects.filter(product=product)
            else:
                return []
        else:
            return ProductImage.objects.all()



class MvtStockViewSet(ModelViewSet):

    serializer_class = MvtStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        pid = self.request.GET.get("pid",False)
        search_date = self.request.GET.get("searchdate",False)
        if pid and search_date:
            product = Product.objects.filter(id = int(pid)).first()
            if product:
                # Assuming search_date is a string in the format "2023-06-28T23%3A00%3A00.000Z"
                decoded_date = unquote(search_date)

                # Convert the decoded string to a datetime object
                search_datetime = datetime.strptime(decoded_date, "%Y-%m-%dT%H:%M:%S.%fZ")

                # Get the start and end of the day
                temp_day = search_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                start_of_day = temp_day + timedelta(days=1)
                print(start_of_day)
                end_of_day = start_of_day + timedelta(days=1)
                print(end_of_day)
                mvt_stocks = MvtStock.objects.filter(product=product,date__gte=start_of_day,
                                                    date__lt=end_of_day).order_by("-date")
                if len(mvt_stocks) > 0:
                    return mvt_stocks
                else:
                    mvt_stocks = MvtStock.objects.filter(product=product,date__lte=start_of_day).order_by("-date")
                    return mvt_stocks
        return []
    
class OptionCategoriesViewSet(ModelViewSet):

    serializer_class = OptionCategoriesSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OptionCategories.objects.all()

class TransportOptionViewSet(ModelViewSet):

    serializer_class = TransportOptionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TransportOption.objects.all()



class ModifyProduct(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,id,format="None"):
        p = Product.objects.filter(p_id = id)
        if len(p) != 0:
            p = p[0]
            data = ProductSerializer(p).data
            C = p.price_achat * p.quantity - p.paid
            provider = p.provider
            provider.credit -= C
            provider.save()
            p.delete()
        else:
            data= {}


        return Response(data, status.HTTP_200_OK)

    def post(self,request,id,format="None"):
        data = request.data
        
        p = Product.objects.filter(p_id = id)[0]
        print(data)
        supplier = Provider.objects.filter(id=data['fournisseur']['id'])[0]
        q = int(data['product']['quantity'])
        credit = ((q - p.quantity) * float(data['product']['price_achat'])) - (float(data['product']['paid']) -  p.paid)
        if (supplier.credit + credit >= 0):
            supplier.credit   += credit
        else:
            supplier.credit = 0
        
        p.provider = supplier
        p.name=data['product']['name']
        p.ptype=data['product']['ptype']
        p.price_vente=data['product']['price_vente']
        p.price_achat=data['product']['price_achat']
        if int(data['product']['quantity']) >= 0:
            p.quantity= int(data['product']['quantity'])
        else:
            return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)
        p.paid  = float(data['product']['paid'])
        #p.place = int(data['product']['place'])
        opt = p.options_set.all()[0]
        opt.metal = data['options']['metal']
        opt.type = data['options']['type']
        p.save()
        supplier.save()
        opt.save()

        resp = {
            'fournisseur':ProviderSerializer(supplier).data,
            'product':ProductSerializer(p).data,
            'options' : OptionsSerializer(opt).data
        }

        return Response(resp,status.HTTP_200_OK)



class OrderProduct(APIView):

    def get(self,request,id,format="None"):
        p = Product.objects.filter(p_id = id)
        if len(p) > 0:
            p = p[0]
            data = ProductSerializer(p).data
        else:
            data = False
        
        return Response(data,status.HTTP_200_OK)
    

    def post(self):
        pass


class OrderV(APIView):
    def get(self,request,format="none"):
        data = request.data
        print(data)
        resp = {}
        return Response(resp,status.HTTP_200_OK)

    def post(self,request,format="None"):
        data = request.data 
        resp = {}
        client = Client.objects.filter(id=data['client']['id'])[0]
        credit = data['sub_options']['total'] - data['sub_options']['paid']
        if (credit > 0):
            client.credit += credit
            client.save()

        resp['client'] = ClientSerializer(client).data
        order = Order.objects.create(client = client,total = data['sub_options']['total'],paid=data['sub_options']['paid'],mode=data['sub_options']['modePayment'])
        while True:
            idd = format_fact(random.randrange(0,99999))
            orders = Order.objects.filter(o_id=idd)
            if len(orders) == 0:
                break
        order.o_id = idd
        resp['order'] = OrderSerializer(order).data
        order.save()
        temp = []
        for prod in data['products']:
            od = OrderDetails.objects.create(order=order, product_name = prod['name'], quantity = prod['quantity'],prix =prod['price_vente'],prix_achat = prod['price_achat'])
            
            p = Product.objects.filter(id=prod['id'])[0]
            od.provider_id = p.provider.id 
            od.product_id = p.id 
            od.save()
            p.quantity -= prod['quantity']
            p.save()
            temp.append(OrderDetailsSerializer(od).data)
            pass

        print(data)
        print(resp)
        return Response(resp,status.HTTP_200_OK)

class DelOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,idd,format=None):
        try:
            order = Order.objects.filter(id=idd)[0]
            c= order.client
            credit = order.total  - order.paid
            c.creadit -=  credit 
            c.save()
            order.delete()
        except:
            return  Response({'response':'failed'},status.HTTP_500_INTERNAL_SERVER_ERROR)



class DelOrderProd(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,orderid,format=None):
        data = request.data
        print(data)
        return Response({'result':'failed'},status.HTTP_500_INTERNAL_SERVER_ERROR)



        
class OrderFilter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format="none"):
        data = request.data
        print(data)
        orders = Order.objects.filter(date__gte=data['startdate'],date__lte = data['enddate']).order_by('-date')
        resp = []
        for order in orders:
            client = ClientSerializer(order.client).data
            o = OrderSerializer(order).data
            details = OrderDetailsSerializer(order.orderdetails_set.all(), many=True).data
            resp.append({
                'client':client,
                'order':o,
                'details' : details
            })
            
        return Response(resp,status.HTTP_200_OK)


class EcheanceFilter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def  get(self,request,format=None):
        invoices =  Invoices.objects.all().order_by('-date')
        ins = InvoiceSerializer(invoices,many=True).data
        return Response(ins,status.HTTP_200_OK)

    def post(self,request,format="none"):
        data = request.data 
        print(data)
        orders = Echeance.objects.filter(dateEcheance__gte=data['startdate'],dateEcheance__lte = data['enddate']).order_by('dateEcheance')
        resp = EcheanceSerializer(orders,many=True).data


        return Response(resp,status.HTTP_200_OK)


class createEchance(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        data = request.data 
        print(data)
        e = Echeance.objects.create(name = data['name'],total = float(data['total']),paid = float(data['paid']),reste = float(data['total']) - float(data['paid']),dateEcheance = data['dateEcheance'],type=data['type'])
        e.save()
        return Response(EcheanceSerializer(e).data,status.HTTP_200_OK)

class ModEcheance(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,id,format=None):
        data = request.data 
        print(data)
        e = Echeance.objects.filter(id=id)[0]
        e.total = float(data['total'])
        e.paid = float(data['paid'])
        e.reste = float(data['total']) - float(data['paid'].split(' ')[0])
        e.dateEcheance = data['dateEcheance']
        e.save()
        return Response(EcheanceSerializer(e).data,status.HTTP_200_OK)

class delEcheance(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,id,format=None):
        e = Echeance.objects.filter(id=id)[0]
        e.delete()
        return Response(EcheanceSerializer(e).data,status.HTTP_200_OK)



class ModOrder(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format="none"):
        data = request.data
        print(data)
        resp = {
            'error':False
        }
        o = Order.objects.filter(o_id = data['details']['o_id'])[0]
        total = 0
        for d in data['details']['details']:
            total += (d['quantity'] * d['prix'])
            od = o.orderdetails_set.filter(id=d['id'])[0]
            
            if od.product_id == -1:
                pass
            else:
                product = Product.objects.filter(id=od.product_id)
                if len(product) == 0:
                    print('product not found')
                else:
                    p = product[0]
                    diff = od.quantity - d['quantity']
                    big_diff = p.quantity + diff
                    if big_diff < 0:
                        return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        p.quantity = big_diff
                        p.save()


            od.quantity = d['quantity']
            od.prix = d['prix']
            od.save()
        print(total)
        print(total)
        
        old_debt = o.total - o.paid
        new_debt = total - (data['details'].get('paid', 0) - data.get('ret', 0)) # new_total - new_paid
        
        # Check if client has changed
        new_client_id = data['details'].get('client_id')
        current_client = o.client
        
        if new_client_id and int(new_client_id) != current_client.id:
            # Client has changed
            try:
                new_client = Client.objects.get(id=int(new_client_id))
                
                # 1. Revert Old Client Debt
                # We subtract the OLD debt from the OLD client's credit (assuming credit = debt balance)
                current_client.credit -= old_debt
                if current_client.credit < 0: current_client.credit = 0 # Safety floor if needed
                current_client.save()
                
                # 2. Apply New Client Debt
                new_client.credit += new_debt
                new_client.save()
                
                # 3. Update Order Client
                o.client = new_client
                
            except Client.DoesNotExist:
                 return Response({'error': True, 'msg': 'New Client not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Same Client - Apply Delta
            # diff = new_debt - old_debt
            # If diff is positive (debt increased), we add to credit.
            # If diff is negative (debt decreased), we subtract (add negative).
            diff = new_debt - old_debt
            
            c = current_client.credit + diff
            if c < 0:
                current_client.credit = 0
            else:
                current_client.credit = c
            current_client.save()

        o.total = total
        o.paid = data['details']['paid']  - data['ret']
        o.mode = data['details']['mode']
        o.transport = data['details']['transport']
        for dl in data['deleted']:
            od = OrderDetails.objects.filter(id=dl['id'])[0]
            if (od.provider_id == -1 and od.product_id == -1):
                resp = {
                    'error':True,
                    'msg' : "Order Ancien"
                }
            else:
                p = Product.objects.filter(id=od.product_id)
                if len(p) == 0:
                    f  =  Provider.objects.filter(id = od.provider_id)
                    if len(f) == 0:
                        resp = {
                    'error':True,
                    'msg' : "Fournisseur Introuvable"
                }
                    else:
                        p  = Product.objects.filter(provider = f[0],name=od.product_name)
                        if len(p) == 0:
                            resp = {
                    'error':True,
                    'msg' : "Produit Introuvable"
                }
                        else:
                            p = p[0]
                else:
                    p  = p[0]
                if p:
                    p.quantity += dl['quantity']
                    p.save()
                od.delete()
                

        o.save()
        if len(data['details']['details']) == 0:
            o.delete()
        return Response(resp , status.HTTP_200_OK)
    

""" class AddDetailsViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class =  GeneralOrderDetailsSerializer
    queryset = OrderDetails.objects.all() """

class AddDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        try:
            data = request.data
            print(data) 
            order = Order.objects.filter(o_id=data['order']).first()
            if order:
                data['order'] = order.id
                print(data)
                od = OrderDetails.objects.filter(order=order.id,product_id=data["product_id"]).first()
                if not od:
                    od_s = GeneralOrderDetailsSerializer(data=data)
                    if  od_s.is_valid():
                        print("valid")
                        od = od_s.save()
                    else:
                        print(od_s.errors)
                        return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    od.quantity += data['quantity']
                    od.save()
                
                order.total +=  data['quantity'] * data['prix']
                order.save()


                product = Product.objects.filter(id=od.product_id)
                if len(product) == 0:
                    print('product not found')
                else:
                    p = product[0]
                    diff =  data['quantity']
                    big_diff = p.quantity - diff
                    if big_diff < 0:
                        od.delete()
                        return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        p.quantity = big_diff
                        p.save()
                    return Response({},status.HTTP_201_CREATED)
                
            else:
                    return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            # ??
            od.delete()
            return Response({},status.HTTP_500_INTERNAL_SERVER_ERROR)

            





def convertdatetime(n):
    m = datetime.min.time()
    return datetime.combine(n,m)

def add_day_date(dt,interval):
    return convertdatetime(dt+ relativedelta(days=interval)) 

def sub_day_date(dt,interval):
    return convertdatetime(dt - relativedelta(days=interval)) 

def add_month_date(dt,interval):
    return convertdatetime(dt+ relativedelta(months=interval)) 

def sub_month_date(dt,interval):
    return convertdatetime(dt- relativedelta(months=interval)) 


def startyear(n):
    return datetime.strptime('{0}-1-1'.format(str(n.year)),"%Y-%d-%m")




class GetClientData(APIView):


    def get(self,request,id,format=None):
        p = Client.objects.filter(id=id)
        if (len(p) > 0):
            resp = {
                "dates" : [],
                "q" : []
            }
            p = p[0]
            now = datetime.now()
            start = sub_month_date(now,1)
            ps  = p.order_set.filter(date__gte=start,date__lte = now)
            for order in ps:
                resp['dates'].append(order.date)
                resp['q'].append(order.total)
            
            return Response(resp,status.HTTP_200_OK)
        else:
            return Response(False,status.HTTP_400_BAD_REQUEST)

class ProductPriceEvolution(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        """
        Returns the price evolution of a specific product for a specific client.
        Payload: { "client_id": int, "product_id": int }
        """
        client_id = request.data.get('client_id')
        product_id = request.data.get('product_id')

        if not client_id or not product_id:
            return Response({'error': 'client_id and product_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client_id = int(client_id)
            product_id = int(product_id)
        except ValueError:
            return Response({'error': 'IDs must be integers'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch orders for this client, ordered by date
        orders = Order.objects.filter(client_id=client_id).order_by('-date')
        
        evolution = []
        for order in orders:
            # Find details for this specific product in the order
            # Note: product_id in OrderDetails is simply an integer field
            details = OrderDetails.objects.filter(order=order, product_id=product_id)
            
            for detail in details:
                evolution.append({
                    'order_id': order.o_id,
                    'date': order.date,
                    'quantity': detail.quantity,
                    'price_sold': detail.prix,
                    'price_bought': detail.prix_achat,
                })

        return Response(evolution, status=status.HTTP_200_OK)


class GetProviderData(APIView):

    def get(self,request,id,format=None):
        p = Provider.objects.filter(id=id)
        if (len(p) > 0):
            resp = {
                "dates" : [],
                "q" : []
            }
            p = p[0]
            now = datetime.now()
            start = sub_month_date(now,1)
            ps  = p.product_set.filter(date__gte=start,date__lte = now)
            for product in ps:
                resp['dates'].append(product.date)
                resp['q'].append(product.quantity)
            
            return Response(resp,status.HTTP_200_OK)
        else:
            return Response(False,status.HTTP_400_BAD_REQUEST)


class GetTop(APIView):

    def get(self,request,format=None):
        resp ={
            'providers_ranks': {
                'providers':[],
                'quantity' :[]
            },
            'clients_ranks':{
                'clients':[],
                'total':[]
            }
        }
        provider_rank = []
        ps = Provider.objects.all()
        for p in ps:
            q = 0
            ps = p.product_set.all()
            for product in ps:
                q += product.quantity
            provider_rank.append({'name':p.name,'q': q})
        newlist = sorted(provider_rank, key=lambda k: k['q'])[::-1]
        resp['providers_ranks']['providers'] = [x['name'] for x in newlist][:5]
        if (any([x['q'] for x in newlist][:5])):
            resp['providers_ranks']['quantity'] = [x['q'] for x in newlist][:5]
        
            

        client_rank = []
        clients = Client.objects.all()
        for client in clients:
            tot = 0
            orders = client.order_set.all()
            for order in orders:
                tot += order.total
            client_rank.append({'name':client.name,'total':tot})
        newlist = sorted(client_rank, key=lambda k: k['total'])[::-1]
        resp['clients_ranks']['clients'] = [x['name'] for x in newlist][:5]
        if (any([x['total'] for x in newlist][:5])):
            resp['clients_ranks']['total'] = [x['total'] for x in newlist][:5]

        return Response(resp,status.HTTP_200_OK)



class GetStable(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self,request,format=None):
        now = datetime.now()
        start_stable = sub_day_date(now,7)
        resp = {
            'ventes':{
                'quantity':0,
                'total' : 0
            },
            'achat':{
                'quantity':0,
                'total' : 0
            },
            'stock':{
                'quantity':0,
                'total' : 0
            },
            'bar':{
                'profit' : [],
                'ventes' : []
            }
        }
        orders = Order.objects.filter(date__gte=start_stable,date__lte = now)
        temp_tot = 0
        temp_q = 0
        for o in orders:
            temp_tot += o.total 
            for od in o.orderdetails_set.all():
                temp_q += od.quantity
        resp['ventes']['total'] = temp_tot
        resp['ventes']['quantity'] = temp_q

        temp_tot = 0
        temp_q = 0
        ps = Product.objects.filter(date__gte=start_stable,date__lte = now)

        for p in ps:
            temp_tot += (p.price_achat * p.quantity)
            temp_q += p.quantity

        resp['achat']['total'] = temp_tot
        resp['achat']['quantity'] = temp_q
        temp_tot = 0
        temp_q = 0
        allps = Product.objects.all()
        for p in allps:
            temp_tot += (p.price_achat * p.quantity)
            temp_q += p.quantity
        resp['stock']['total'] = temp_tot
        resp['stock']['quantity'] = temp_q
        data = {}
        start = startyear(now)
        for _ in range(1,13):
            end_date = add_month_date(start,1)
            #print(str(s) + ' ==> ' + str(end_date))
            orders = Order.objects.filter(date__gte=start,date__lte = end_date)
            v = 0
            profit = 0
            for order in orders:
                for od in order.orderdetails_set.all():
                    v += od.quantity
                    if od.prix < od.prix_achat:
                        print('here')
                        print(od.product_name)
                        print(od.prix)
                        print(od.prix_achat)
                    profit += ( (od.quantity * od.prix) - (od.quantity * od.prix_achat))
            resp['bar']['profit'].append(profit)
            resp['bar']['ventes'].append(v)

            start = end_date

        return Response(resp,status.HTTP_200_OK)


class GetOrderSalesData(APIView):


    def get(self,request,format=None):
        # Define the current date
        today = timezone.now()  # Replace with timezone.now() in production

        # Generate a list of all months in the last 12 months
        all_months = []
        current_month = today.replace(day=1)  # Start from the first day of the current month
        for _ in range(12):
            all_months.append(current_month.strftime("%m/%Y"))  # Add the month/year to the list
            # Move to the previous month
            if current_month.month == 1:
                current_month = current_month.replace(year=current_month.year - 1, month=12)
            else:
                current_month = current_month.replace(month=current_month.month - 1)
        all_months.reverse()  # Ensure the months are in chronological order

        # Calculate the start of the current month
        start_of_current_month = today.replace(day=1)

        # Use the first month in `all_months` to define `twelve_months_ago`
        twelve_months_ago = datetime.strptime(all_months[0], "%m/%Y").replace(day=1)

        # Query OrderDetails from the last 12 months
        orders_last_12_months = OrderDetails.objects.filter(
            order__date__gte=twelve_months_ago,order__date__lte=today
        ).select_related('order')
        print(orders_last_12_months)

        # Prepare a nested dictionary to store results
        sales_data = defaultdict(lambda: defaultdict(lambda: {"total_sales": 0, "total_quantity": 0}))

        # Process each OrderDetail record
        for detail in orders_last_12_months:
            # Extract the month/year from the order date
            order_date = detail.order.date
            month_year = order_date.strftime("%m/%Y")  # Format: "MM/YYYY"

            # Calculate the total sales and total quantity for this product in this month
            total_sales = detail.prix * detail.quantity
            total_quantity = detail.quantity

            # Use product_name as the key
            product_name = detail.product_name

            # Update the nested dictionary
            sales_data[product_name][month_year]["total_sales"] += total_sales
            sales_data[product_name][month_year]["total_quantity"] += total_quantity

        

        # Fill in missing months with zeros
        result = {}
        # Initialize a dictionary with all months set to zero
        filled_data = {month: {"total_sales": 0, "total_quantity": 0} for month in all_months}
        #result[product_name] = filled_data
        for product_name, monthly_data in sales_data.items():
            filled_data = {month: {"total_sales": 0, "total_quantity": 0} for month in all_months}
            # Update with actual data where available
            for month, data in monthly_data.items():
                filled_data[month] = data
            result[product_name] = filled_data

        return Response(result,status.HTTP_200_OK)

class GetTopProducts(APIView):

    def get(self,request,format=None):
        # Define the current date
        today = timezone.now()  # Replace with timezone.now() in production
        twelve_months_ago = today - timedelta(days=365)

        # Query the top 5 products sold in the last 12 months
        top_products = (
            OrderDetails.objects.filter(order__date__gte=twelve_months_ago)
            .values('product_name')  # Group by product_name
            .annotate(total_quantity=Sum('quantity'))  # Sum the quantity for each product
            .order_by('-total_quantity')  # Sort by total_quantity in descending order
            .values('product_name', 'total_quantity')[:5]  # Limit to top 5
        )

        # Convert the queryset to a list of dictionaries
        result = list(top_products)
        return Response(result,status.HTTP_200_OK)