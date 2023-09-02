from django.db.models.base import Model
from rest_framework.serializers import ModelSerializer,SerializerMethodField
from .models import CustomUser,Product,Provider,Options,Invoices,Client,Order,OrderDetails,Echeance,MvtStock,OptionCategories,ProductImage,TransportOption



class RegisterSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','email','password']
        extra_kwargs = {'password': {'write_only':True}}

    def create(self,validated,*args,**kwargs):
        u = CustomUser.objects.create(username = validated['username'],email=validated['email'])
        u.set_password(validated['password'])
        u.save()

        return RegisterSerializer(u).data




class ProviderSerializer(ModelSerializer):
    class Meta:
        model = Provider
        fields = ['id','name','email','credit','phone','address','date']

class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['id','name','email','credit','phone','address','date']
        
class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','total','paid','mode','transport','o_id','date']

class OrderDetailsSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['id','product_name','quantity','prix','prix_achat','provider_id','product_id']

class GeneralOrderDetailsSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = "__all__"

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','p_id','name','paid','ptype','price_vente','price_achat','quantity']

class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductWithImageSerializer(ModelSerializer):

    images = SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
    
    def get_images(self,instance):
        storedImages = ProductImage.objects.filter(product=instance)
        if len(storedImages) > 0:
            res = []
            for storedImage in storedImages:
                res.append(ProductImageSerializer(storedImage).data)
            return res
        else:
            return []



class OptionsSerializer(ModelSerializer):
    class Meta:
        model = Options
        fields = ['id','metal','type']


class  InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoices
        fields = ['id','f_id','path','date']

class EcheanceSerializer(ModelSerializer):
    class Meta:
        model = Echeance
        fields = ['id','name','total','paid','reste','dateEcheance','date']

class MvtStockSerializer(ModelSerializer):

    class Meta:
        model = MvtStock
        fields = "__all__"

class OptionCategoriesSerializer(ModelSerializer):

    class Meta:
        model = OptionCategories
        fields = "__all__"


class TransportOptionsSerializer(ModelSerializer):

    class Meta:
        model = TransportOption
        fields = "__all__"


