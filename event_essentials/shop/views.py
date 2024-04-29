from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate,signup
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt  #give a free space for csrf token
from PayTm import Checksum
from django.contrib import messages 
MERCHANT_KEY='kbzk1DSbJiv_03p5'

def LoginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = signup.objects.get(username=username)  # Use get() instead of filter().first()
            if user.passwd == password:
                request.session['username'] = username
                return redirect('/shop')  # Redirect to your home page or dashboard
            else:
                messages.error(request, 'Invalid password')  # Display error message for incorrect password
        except signup.DoesNotExist:
            messages.error(request, 'Invalid username')  # Display error message for invalid username
    return render(request, "shop/login.html")


def SignupPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        else:
            signup.objects.create(username=username, email=email, passwd=password1)
            messages.success(request, 'Account created successfully')
            return redirect('login')
    return render(request, "shop/signup.html")





def index(request):
    # products= Product.objects.all()
    # print(products)   
    allProds = []
    catprods = Product.objects.values('category','product_id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n= len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod,range(1,nSlides),nSlides])
        
    # params={'no_of_slides':nSlides, 'range':range(1,nSlides), 'product': products}
    # allProds = [[products,range(1,nSlides),nSlides],[products,range(1,nSlides),nSlides]]
    params = {'allProds':allProds}
    return render(request,"shop/index.html", params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    thank = False
    if request.method == 'POST':
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone_no=request.POST.get('phone_number','')
        desc = request.POST.get('desc','')
        print(name , email, phone_no, desc)
        contact = Contact(name=name, email=email, phone_no=phone_no, desc=desc)
        contact.save()
        thank = True
    return render(request,'shop/contact.html',{'thank':thank})

#def rent(request):
    #return render(request,'shop/rent.html')
def rent_item(request, item_id):
    item = get_object_or_404(Product, pk=item_id)  # Assuming your model is named Product
    context = {'item': item}
    #return render(request, 'rent_item_form.html', context)
    return render(request, 'shop/rent_item_form.html', context)



def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        # return HttpResponse(f"{orderId} and {email}")
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def search(request):
    return render(request,'shop/search.html')

def products(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})



def checkout(request):
    if request.method=="POST":
        items_json= request.POST.get('itemsJson', '')
        name=request.POST.get('name', '')
        amount=request.POST.get('amount', '')
        email=request.POST.get('email', '')
        address=request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        phone=request.POST.get('phone', '')
        order = Orders(items_json= items_json, name=name, amount=amount , email=email, address= address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()
        update= OrderUpdate(order_id= order.order_id, update_desc="The order has been placed")
        update.save()
        thank=True
        id=order.order_id
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
        #Request paytm to transfer the amount to your account after payment by user 
        param_dict = {
            'MID': 'WorldP64425807474247', #here id merchant ID. here is default merchant Id
            'ORDER_ID': str(order.order_id), #here is my order id
            'TXN_AMOUNT': str(amount),
            'CUST_ID': 'email', #customer email
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING', #for the testing
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request,'shop/paytm.html',{'param_dict':param_dict})
    return render(request, 'shop/checkout.html')



@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})