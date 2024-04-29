from django.urls import path
from . import views
from Crypto.Cipher import AES


urlpatterns = [
   
    path("",views.index,name="ShopHome"),
    path("about/",views.about,name="AboutUs"),
    path("contact/",views.contact,name="ContactUs"),
    path("tracker/",views.tracker,name="Tracker"),
    path("search/",views.search,name="Search"),
    path("products/<int:myid>",views.products,name="productview"),
    path("checkout/",views.checkout,name="Checkout"),
    #path("rent/",views.rent,name="rent"),
    path('rent/<int:item_id>/', views.rent_item, name='rent_item'),
    path('handlerquest/',views.handlerequest, name = "HandleRequest"),
    # path("login/", views.login, name="Login"),
    # path("signup/", views.signup, name="Signup")
    
]
