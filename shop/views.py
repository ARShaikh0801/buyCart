from math import ceil
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Product,Contact,Order,OrderUpdate,Rating
import json
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.http import require_POST

# Create your views here.
def index(request):
    allProds=[]
    catProds=Product.objects.values('category','id')

    cat_sub_map = defaultdict(set)
    for item in Product.objects.values('category', 'subcategory'):
        cat_sub_map[item['category']].add(item['subcategory'])

    cat_sub_map = {k: list(v) for k, v in cat_sub_map.items()}

    cats={item['category'] for item in catProds}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1,nSlides),nSlides])
    
    available_Cats=Product.objects.values('category').distinct()
    available_subCats=Product.objects.values('subcategory').distinct()
    
    params={'allProds':allProds,'available_Cats':available_Cats,'available_subCats':available_subCats,'categories':"AllCats",'subCategories':"AllSubs",'sizes':"AllSizes",'ratings':"AllRates",'priceRange':"AllPrices",'cat_sub_map': json.dumps(cat_sub_map)}  

    return render(request,'shop/index.html',params)

def filters(request):
    if request.method=="POST":
        products=Product.objects.all()
        cat_sub_map = defaultdict(set)

        for item in Product.objects.values('category', 'subcategory'):
            cat_sub_map[item['category']].add(item['subcategory'])

        cat_sub_map = {k: list(v) for k, v in cat_sub_map.items()}

        categories=request.POST.get('categories')
        subCategories=request.POST.get('subCategories')
        sizes=request.POST.get('sizes')
        ratings=request.POST.get('ratings')
        priceRange=request.POST.get('priceRange')
        if categories=="AllCats" and subCategories=="AllSubs" and sizes=="AllSizes" and ratings=="AllRates" and priceRange=="AllPrices":
            return redirect('ShopHome')
        if categories and categories!="AllCats":
            products=products.filter(category=categories)
        if subCategories and subCategories!="AllSubs":
            products=products.filter(subcategory=subCategories)

        if sizes and sizes != "AllSizes":
            products = products.filter(available_sizes__icontains=sizes)

        if ratings and ratings != "AllRates":
            if ratings == "2":
                products = products.filter(prodRating__lte=3)
            else:
                products = products.filter(prodRating__gte=int(ratings))

        if priceRange and priceRange != "AllPrices":
            priceRange = int(priceRange)
            if priceRange == 500:
                products = products.filter(finalPrice__lte=500)
            elif priceRange == 1000:
                products = products.filter(finalPrice__gt=500, finalPrice__lte=1000)
            elif priceRange == 2000:
                products = products.filter(finalPrice__gt=1000, finalPrice__lte=2000)
            elif priceRange == 5000:
                products = products.filter(finalPrice__gt=2000, finalPrice__lte=5000)
            elif priceRange == 6000:
                products = products.filter(finalPrice__gte=5000)
        
        cats = products.values_list('category', flat=True).distinct()
        allProds=[]
        available_Cats=Product.objects.values('category').distinct()
        available_subCats=Product.objects.values('subcategory').distinct()
        
        if not cats:
            messages.error(request,"No Products Found")
            return render(request, "shop/index.html", {'allProds':allProds,'available_Cats':available_Cats,'available_subCats':available_subCats,'categories':categories,'subCategories':subCategories,'sizes':sizes,'ratings':ratings,'priceRange':priceRange,'cat_sub_map': json.dumps(cat_sub_map)})
        
        for cat in cats:
            prod=products.filter(category=cat)
            n=len(products)
            nSlides=n//4 + ceil((n/4)-(n//4))
            allProds.append([prod, range(1,nSlides),nSlides])
    
    
        params={'allProds':allProds,'available_Cats':available_Cats,'available_subCats':available_subCats,'categories':categories,'subCategories':subCategories,'sizes':sizes,'ratings':ratings,'priceRange':priceRange,'cat_sub_map': json.dumps(cat_sub_map)}
    
        return render(request, "shop/index.html", params)

    return redirect('ShopHome')
        
    

def searchMatch(query,item):
    if query in item.product_name.lower() or query in item.desc.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    else:
        return False

def search(request):
    query=request.GET.get('search')
    allProds=[]
    catProds=Product.objects.values('category','id')
    cats={item['category'] for item in catProds}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query,item)]
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        if len(prod)!=0:
            allProds.append([prod, range(1,nSlides),nSlides])
    params={'allProds':allProds}
    if len(allProds)==0 or len(query)<2:
        params={}
        messages.error(request,"No Match Found")
        return redirect('ShopHome')
    return render(request,'shop/search.html',params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.user.is_authenticated:
        prevMsgs=Contact.objects.filter(email=request.user.email).order_by('-timeStamp')
        if request.method=="POST":
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone','')
            desc=request.POST.get('desc','')
            contact=Contact(name=name,email=email,phone=phone,desc=desc)
            contact.save()
            messages.success(request,"Your message has been sent")
            return render(request,'shop/contact.html',{'prevMsgs':prevMsgs})
    else:
        prevMsgs=[]
        messages.error(request,"Login To Contact Us or To View Previous Messages")
   
    return render(request,'shop/contact.html',{'prevMsgs':prevMsgs})

def tracker(request):

    if request.user.is_authenticated:
        Order.objects.filter(email=request.user.email,payment_status__in=["", "pending"]).delete()
        try:
            email = request.user.email
            orders = Order.objects.filter(email=email)
            if len(orders) > 0:
                finalDict = {}
                for prod in orders:
                    products_list = []
                    try:
                        items = json.loads(prod.items_json)
                        for item_key, item_data in items.items():
                            pid = item_key.replace('pr', '')   
                            try:
                                product = Product.objects.get(id=pid)
                                products_list.append({
                                    "name": product.product_name,
                                    "qty": item_data[0],          
                                    "price": product.finalPrice,
                                    "image": product.main_image.url,
                                    "size": item_data[3],
                                })
                            except Product.DoesNotExist:
                                pass
                    except Exception:
                        products_list = []

                    orderId = prod.order_id
                    update_qs = OrderUpdate.objects.filter(order_id=orderId)
                    updates = []
                    for item in update_qs:
                        updates.append({
                            'text': item.update_desc,
                            'time': item.timestamp,
                        })
                    finalDict[prod] = {
                        "updates": updates,
                        "products": products_list,
                    }
                return render(request, 'shop/tracker.html', {"finalDict": finalDict})
            else:
                messages.success(request, "You did not order anything...")
                return render(request, 'shop/tracker.html', {"finalDict": {}})
        except Exception as e:
            print("Tracker error:", e)
            messages.error(request, "Unable to fetch your orders...")
            return render(request, 'shop/tracker.html', {"finalDict": {}})
    else:
        messages.error(request, "Login to track your orders...")
    return render(request, 'shop/tracker.html', {"finalDict": {}})

def productView(request,myid):
    product=Product.objects.filter(id=myid)
    return render(request,'shop/prodView.html', {'product':product[0]})

def checkout(request):
    if request.method=="POST":
        items_json=request.POST.get('itemsJson','')
        name = request.user.get_full_name()
        email = request.user.email
        amount=request.POST.get('amount','')
        address=request.POST.get('address1','')+ " " + request.POST.get('address2','')
        city=request.POST.get('city','')
        state=request.POST.get('state','')
        zip_code=request.POST.get('zip_code','')
        phone=request.POST.get('phone','')
        try:
            order=Order(items_json=items_json,name=name,amount=amount,email=email,phone_no=phone,address=address,city=city,state=state,zip_code=zip_code,payment_status="")
            order.save()
            update=OrderUpdate(order_id=order.order_id,update_desc="The order has been placed")
            update.save()
            dummy=request.POST.get('dummy','false')
            return render(request,'shop/gateway.html',{'info':[order.order_id,amount,dummy]})
        except:
            messages.error(request,"Server is not responding...")
            return render(request,'shop/checkout.html')
    return render(request,'shop/checkout.html')

def handlePayment(request):
    if request.method=="POST":
        payment=request.POST.get('inlineRadioOptions')
        order=Order.objects.get(order_id=request.POST.get('orderId'))
        payment_status="pending"
        if(payment=='cod'):
            payment_status="Cash On Delhivery"
            order.payment_status=payment_status
            order.save()
            messages.success(request,"Your Cash On Delhivery Order Placed Successfully...")
            return redirect('ShopHome')
        elif(payment=='upi'):
            upi_id=request.POST.get('upi-id')
            gpay=request.POST.get('RadioOptions')
            if((gpay and (not upi_id)) or (upi_id and (not gpay))):
                payment_status="UPI Payment Done"
                order.payment_status=payment_status
            else:
                messages.error(request,"Please select only 1 option for upi payment (note : if qr-code selected then do not enter upi-id)")
                return render(request,'shop/gateway.html')
            order.save()
            messages.success(request,"Your Order Placed Successfully...")
        order.save()
        return redirect('ShopHome')
    return render(request,'shop/gateway.html')

@require_POST
def rateProduct(request):
    product_id = request.POST.get('prodId')
    product = Product.objects.get(id=product_id)
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        rate = int(request.POST.get('rate'))
        review = request.POST.get('review')


        rating, created = Rating.objects.get_or_create(user=user,product=product,defaults={'rating': rate,'review': review})

        if not created:
            messages.error(request, "You have already rated this product")
            return redirect('ProductView', product.id)

        product.prodRating = ((product.prodRating * product.ratingCount) + rate) / (product.ratingCount + 1)

        product.ratingCount += 1
        product.save()

        messages.success(request, "Thank you for your review!")
        return redirect('ProductView', product.id)

    elif not request.user.is_authenticated:
        messages.error(request, "You must be logged in to rate a product")
    return redirect('ProductView', product.id)


def handleSignup(request):
    if request.method=='POST':
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        checkUser=User.objects.filter(username=username)
        checkEmail=User.objects.filter(email=email)
        if checkUser.count():
            messages.error(request,"Username Already Exists")
            return redirect('ShopHome')
        if checkEmail.count():
            messages.error(request,"Email Already Exists")
            return redirect('ShopHome')
        if len(username)>10:
            messages.error(request,"Username Must Be Less Than 10 Character")
            return redirect('ShopHome')
        if not username.isalnum():
            messages.error(request,"Username Should Contain Letters And Numbers Only")
            return redirect('ShopHome')
        if pass1!=pass2:
            messages.error(request,"Password Do Not Match")
            return redirect('ShopHome')
        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.save()
        messages.success(request,"Your buyCart Account Is Successfully Created")
        user=authenticate(username=username,password=pass1)
        login(request,user)
        return redirect('ShopHome')
    else:
        return HttpResponse('404-Not Found')

def handleLogin(request):
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpass=request.POST['loginpass']
        user=authenticate(username=loginusername,password=loginpass)
        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged In")
        else:
            messages.error(request,"Invalid Credentials")
        return redirect('ShopHome')
    return HttpResponse('404-Not Found')

def handleLogout(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('ShopHome')

