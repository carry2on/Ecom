from django.shortcuts import render, redirect
from django.contrib import messages
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
def not_shipped_dash(req):
    if req.user.is_authenticated and req.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        
        # ADDED: Listen for the "Mark Shipped" button click!
        if req.method == "POST":
            # Get the order ID from the hidden form input
            num = req.POST.get('num')
            
            # Grab the specific order and update it
            order = Order.objects.get(id=num)
            order.shipped = True
            
            # Because you set up that awesome Python signal in models.py, 
            # calling .save() will automatically stamp the current date and time!
            order.save() 
            
            messages.success(req, "Order Marked as Shipped!")
            return redirect('not_shipped_dash')

        return render(req, "payment/not_shipped_dash.html", {"orders": orders})
    else:
        messages.success(req, "Access Denied")
        return redirect('home')

def shipped_dash(req):
    if req.user.is_authenticated and req.user.is_superuser:
        # Grab all orders where shipped is True
        orders = Order.objects.filter(shipped=True)
        return render(req, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.success(req, "Access Denied")
        return redirect('home')
def payment_success(req):
    return render(req, 'payment/payment_success.html')

def checkout(req):
    cart = Cart(req)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if req.user.is_authenticated:
        shipping_user, created = ShippingAddress.objects.get_or_create(user=req.user)
        shipping_form = ShippingForm(req.POST or None, instance=shipping_user)
    else:
        shipping_form = ShippingForm(req.POST or None)

    return render(req, 'payment/checkout.html', {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form
    })

def billing_info(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Capture shipping info and convert it to a standard dictionary
        shipping_info = request.POST.dict()
        request.session['my_shipping'] = shipping_info
        
        # Load the Payment Form
        billing_form = PaymentForm()
        
        return render(request, "payment/billing_info.html", {
            "cart_products": cart_products, 
            "quantities": quantities, 
            "totals": totals, 
            "shipping_info": shipping_info,
            "billing_form": billing_form
        })
    else:
        messages.error(request, "Access Denied")
        return redirect('home')

def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        payment_form = PaymentForm(request.POST or None)
        
        # Grab the shipping data we safely saved in the session
        my_shipping = request.session.get('my_shipping')

        # Use .get() to prevent crashes if a field is missing
        full_name = my_shipping.get('shipping_full_name', '')
        email = my_shipping.get('shipping_email', '')
        
        # Combine shipping address
        shipping_address = f"{my_shipping.get('shipping_address1', '')}\n{my_shipping.get('shipping_address2', '')}\n{my_shipping.get('shipping_city', '')}\n{my_shipping.get('shipping_state', '')}\n{my_shipping.get('shipping_zipcode', '')}\n{my_shipping.get('shipping_country', '')}"
        
        amount_paid = totals

        # 1. CREATE THE ORDER
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
        else:
            create_order = Order(fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
        
        create_order.save()
        order_id = create_order.pk

        # 2. CREATE THE ORDER ITEMS
        for product in cart_products:
            product_id = product.id
            if product.is_sales:
                price = product.sale_price
            else:
                price = product.price

            for key, value in quantities.items():
                if int(key) == product.id:
                    create_order_item = OrderItem(
                        order_id=order_id, 
                        product_id=product_id, 
                        user=request.user if request.user.is_authenticated else None, 
                        quantity=value['qty'], 
                        price=price
                    )
                    create_order_item.save()

        # 3. DELETE THE CART
        for key in list(request.session.keys()):
            if key == "session_key":
                del request.session[key]

        messages.success(request, "Order Placed Successfully!")
        return redirect('payment_success')
        
    else:
        messages.error(request, "Access Denied")
        return redirect('home')
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # 1. Grab the specific order
        order = Order.objects.get(id=pk)
        
        # 2. Grab all the items attached to that specific order
        items = OrderItem.objects.filter(order=pk)

        # 3. Handle the form to update Shipping Status
        if request.method == "POST":
            status = request.POST.get('shipping_status')
            
            # Check if they selected Shipped or Un-Shipped
            if status == "true":
                order.shipped = True
            else:
                order.shipped = False
                
            # Save it! (Your Python signal from models.py will automatically handle the date!)
            order.save()
            messages.success(request, "Shipping Status Updated!")
            return redirect('home')

        return render(request, 'payment/orders.html', {"order": order, "items": items})
        
    else:
        messages.error(request, "Access Denied")
        return redirect('home')
# ######################################
# Razorpay Integration Code Below
# #####################################

# import razorpay
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from cart.cart import Cart
# from .forms import ShippingForm
# from .models import ShippingAddress, Order, OrderItem

# # Initialize the Razorpay Client
# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def payment_success(request):
#     return render(request, 'payment/payment_success.html')

# def checkout(request):
#     cart = Cart(request)
#     cart_products = cart.get_prods()
#     quantities = cart.get_quants()
#     totals = cart.cart_total()

#     if request.user.is_authenticated:
#         shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
#         shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
#     else:
#         shipping_form = ShippingForm(request.POST or None)

#     return render(request, 'payment/checkout.html', {
#         'cart_products': cart_products,
#         'quantities': quantities,
#         'totals': totals,
#         'shipping_form': shipping_form,
#     })

# def not_shipped_dash(req):
#     if req.user.is_authenticated and req.user.is_superuser:
#         orders = Order.objects.filter(shipped=False)
#         if req.method == 'POST':
#             num = req.POST.get('num')
#             order = Order.objects.get(id=num)
#             order.shipped = True
#             order.save()
#             messages.success(req, 'Order Marked as Shipped!')
#             return redirect('not_shipped_dash')
#         return render(req, 'payment/not_shipped_dash.html', {'orders': orders})
#     else:
#         messages.success(req, 'Access Denied')
#         return redirect('home')

# def shipped_dash(req):
#     if req.user.is_authenticated and req.user.is_superuser:
#         orders = Order.objects.filter(shipped=True)
#         return render(req, 'payment/shipped_dash.html', {'orders': orders})
#     else:
#         messages.success(req, 'Access Denied')
#         return redirect('home')

# def orders(req, pk):
#     if req.user.is_authenticated and req.user.is_superuser:
#         order = Order.objects.get(id=pk)
#         items = OrderItem.objects.filter(order=pk)
#         if req.method == 'POST':
#             status = req.POST.get('shipping_status')
#             order.shipped = True if status == 'true' else False
#             order.save()
#             messages.success(req, 'Shipping Status Updated!')
#             return redirect('home')
#         return render(req, 'payment/orders.html', {'order': order, 'items': items})
#     else:
#         messages.error(req, 'Access Denied')
#         return redirect('home')

# def billing_info(request):
#     if request.method == "POST":
#         cart = Cart(request)
#         cart_products = cart.get_prods()
#         quantities = cart.get_quants()
#         totals = cart.cart_total()

#         # Capture shipping info and convert it to a standard dictionary
#         shipping_info = request.POST.dict()
#         request.session['my_shipping'] = shipping_info
        
#         # 1. Calculate Amount in Paise (Razorpay requires amounts in paise/cents)
#         # Assuming totals is a float/decimal like 2006.08
#         amount_in_paise = int(float(totals) * 100) 
        
#         # 2. Create the Razorpay Order
#         razorpay_order = client.order.create({
#             "amount": amount_in_paise,
#             "currency": "INR",
#             "payment_capture": "1" # Auto-capture payment
#         })
        
#         # 3. Grab the generated Order ID to send to the frontend
#         razorpay_order_id = razorpay_order['id']
        
#         return render(request, "payment/billing_info.html", {
#             "cart_products": cart_products, 
#             "quantities": quantities, 
#             "totals": totals, 
#             "shipping_info": shipping_info,
#             "razorpay_order_id": razorpay_order_id,
#             "razorpay_amount": amount_in_paise,
#             "razorpay_key_id": settings.RAZORPAY_KEY_ID,
#         })
#     else:
#         messages.error(request, "Access Denied")
#         return redirect('home')

# def process_order(request):
#     if request.method == "POST":
        
#         # 1. Grab Razorpay details from the successful payment
#         payment_id = request.POST.get('razorpay_payment_id', '')
#         razorpay_order_id = request.POST.get('razorpay_order_id', '')
#         signature = request.POST.get('razorpay_signature', '')
        
#         # 2. Verify the payment signature to ensure it wasn't tampered with
#         params_dict = {
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature
#         }
        
#         try:
#             client.utility.verify_payment_signature(params_dict)
#             # IF SUCCESSFUL: Do all your normal database saving!
            
#             cart = Cart(request)
#             cart_products = cart.get_prods()
#             quantities = cart.get_quants()
#             totals = cart.cart_total()

#             my_shipping = request.session.get('my_shipping')
#             full_name = my_shipping.get('shipping_full_name', '')
#             email = my_shipping.get('shipping_email', '')
#             shipping_address = f"{my_shipping.get('shipping_address1', '')}\n{my_shipping.get('shipping_address2', '')}\n{my_shipping.get('shipping_city', '')}\n{my_shipping.get('shipping_state', '')}\n{my_shipping.get('shipping_zipcode', '')}\n{my_shipping.get('shipping_country', '')}"
#             amount_paid = totals

#             # Create the Order
#             if request.user.is_authenticated:
#                 create_order = Order(user=request.user, fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
#             else:
#                 create_order = Order(fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
#             create_order.save()
            
#             order_id = create_order.pk

#             # Create Order Items
#             for product in cart_products:
#                 price = product.sale_price if product.is_sales else product.price
#                 for key, value in quantities.items():
#                     if int(key) == product.id:
#                         create_order_item = OrderItem(
#                             order_id=order_id, 
#                             product_id=product.id, 
#                             user=request.user if request.user.is_authenticated else None, 
#                             quantity=value['qty'], 
#                             price=price
#                         )
#                         create_order_item.save()

#             # Empty Cart
#             for key in list(request.session.keys()):
#                 if key == "session_key":
#                     del request.session[key]

#             messages.success(request, "Payment Successful & Order Placed!")
#             return redirect('payment_success')
            
#         except razorpay.errors.SignatureVerificationError:
#             messages.error(request, "Payment Verification Failed! Do not tamper with data.")
#             return redirect('home')
        
#     else:
#         messages.error(request, "Access Denied")
#         return redirect('home')

















