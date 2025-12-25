from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from rest_framework import routers

router = routers.SimpleRouter()
router.register("mvtstock",MvtStockViewSet,basename="Stock changes")
router.register("option",OptionCategoriesViewSet,basename="Option manager")
router.register("transport",TransportOptionViewSet,basename="Transport manager")
router.register("upload",ProductImageViewSet,basename="Image manager")
#router.register("detailsadd",AddDetailsViewSet,basename="Details manager")



urlpatterns = [
    path("",include(router.urls)),
    path('register',Register.as_view()),
    path('token',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('session',TestSession.as_view()),
    path('provider',AddProvider.as_view()),
    path('modprovider/<int:id>',ModifyProvider.as_view()),
    path('provider-products',getProviderProducts.as_view()),
    path('client',AddClient.as_view()),
    path('getclients',OpenClient.as_view()),
    path('modclient/<int:id>',ModifyClient.as_view()),
    path('product',AddProduct.as_view()),
    path('silentpd',SilentGetProducts.as_view()),
    path('silentdetails',SilentGetInfo.as_view()),
    path('detailsadd/',AddDetails.as_view()),
    
    path('modproduct/<str:id>',ModifyProduct.as_view()),
    path('getproduct/<str:id>',OrderProduct.as_view()),
    # get products via ids
    path("silentProducts/getinfo",SilentGetProductsInfo.as_view()),

    # order urls 
    path('order',OrderV.as_view()),
    path('filterorder',OrderFilter.as_view()),
    path('modorder',ModOrder.as_view()),
    path('delorder/<int:id>',DelOrderProd.as_view()),

    # download barcode labels
    path('downloadbr',postDownload.as_view()),

    # Echeance views 
    path('echeancesfilter',EcheanceFilter.as_view()),
    path('createecheance',createEchance.as_view()),
    path('modecheance/<int:id>',ModEcheance.as_view()),
    path('delecheance/<int:id>',delEcheance.as_view()),



    ###
    path('download/<str:id>',Download.as_view()),
    ## analytics views 
    path('getstable',GetStable.as_view()),
    path('getsalestats',GetOrderSalesData.as_view()),
    path('gettop5',GetTopProducts.as_view()),
    path('getranks',GetTop.as_view()),
    path('getproviderdata/<int:id>',GetProviderData.as_view()),
    path('getclientdata/<int:id>',GetClientData.as_view()),
    path('price-evolution',ProductPriceEvolution.as_view()),

]
