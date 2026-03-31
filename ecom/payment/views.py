# from django.shortcuts import render, redirect
# from django.contrib import messages
# from cart.cart import Cart
# from .forms import ShippingForm, PaymentForm
# from .models import ShippingAddress, Order, OrderItem
# def not_shipped_dash(req):
#     if req.user.is_authenticated and req.user.is_superuser:
#         orders = Order.objects.filter(shipped=False)
        
#         # ADDED: Listen for the "Mark Shipped" button click!
#         if req.method == "POST":
#             # Get the order ID from the hidden form input
#             num = req.POST.get('num')
            
#             # Grab the specific order and update it
#             order = Order.objects.get(id=num)
#             order.shipped = True
            
#             # Because you set up that awesome Python signal in models.py, 
#             # calling .save() will automatically stamp the current date and time!
#             order.save() 
            
#             messages.success(req, "Order Marked as Shipped!")
#             return redirect('not_shipped_dash')

#         return render(req, "payment/not_shipped_dash.html", {"orders": orders})
#     else:
#         messages.success(req, "Access Denied")
#         return redirect('home')

# def shipped_dash(req):
#     if req.user.is_authenticated and req.user.is_superuser:
#         # Grab all orders where shipped is True
#         orders = Order.objects.filter(shipped=True)
#         return render(req, "payment/shipped_dash.html", {"orders": orders})
#     else:
#         messages.success(req, "Access Denied")
#         return redirect('home')
# def payment_success(req):
#     return render(req, 'payment/payment_success.html')

# def checkout(req):
#     cart = Cart(req)
#     cart_products = cart.get_prods()
#     quantities = cart.get_quants()
#     totals = cart.cart_total()

#     if req.user.is_authenticated:
#         shipping_user, created = ShippingAddress.objects.get_or_create(user=req.user)
#         shipping_form = ShippingForm(req.POST or None, instance=shipping_user)
#     else:
#         shipping_form = ShippingForm(req.POST or None)

#     return render(req, 'payment/checkout.html', {
#         "cart_products": cart_products,
#         "quantities": quantities,
#         "totals": totals,
#         "shipping_form": shipping_form
#     })

# def billing_info(request):
#     if request.method == "POST":
#         cart = Cart(request)
#         cart_products = cart.get_prods()
#         quantities = cart.get_quants()
#         totals = cart.cart_total()

#         # Capture shipping info and convert it to a standard dictionary
#         shipping_info = request.POST.dict()
#         request.session['my_shipping'] = shipping_info
        
#         # Load the Payment Form
#         billing_form = PaymentForm()
        
#         return render(request, "payment/billing_info.html", {
#             "cart_products": cart_products, 
#             "quantities": quantities, 
#             "totals": totals, 
#             "shipping_info": shipping_info,
#             "billing_form": billing_form
#         })
#     else:
#         messages.error(request, "Access Denied")
#         return redirect('home')

# def process_order(request):
#     if request.POST:
#         cart = Cart(request)
#         cart_products = cart.get_prods()
#         quantities = cart.get_quants()
#         totals = cart.cart_total()

#         payment_form = PaymentForm(request.POST or None)
        
#         # Grab the shipping data we safely saved in the session
#         my_shipping = request.session.get('my_shipping')

#         # Use .get() to prevent crashes if a field is missing
#         full_name = my_shipping.get('shipping_full_name', '')
#         email = my_shipping.get('shipping_email', '')
        
#         # Combine shipping address
#         shipping_address = f"{my_shipping.get('shipping_address1', '')}\n{my_shipping.get('shipping_address2', '')}\n{my_shipping.get('shipping_city', '')}\n{my_shipping.get('shipping_state', '')}\n{my_shipping.get('shipping_zipcode', '')}\n{my_shipping.get('shipping_country', '')}"
        
#         amount_paid = totals

#         # 1. CREATE THE ORDER
#         if request.user.is_authenticated:
#             user = request.user
#             create_order = Order(user=user, fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
#         else:
#             create_order = Order(fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
        
#         create_order.save()
#         order_id = create_order.pk

#         # 2. CREATE THE ORDER ITEMS
#         for product in cart_products:
#             product_id = product.id
#             if product.is_sales:
#                 price = product.sale_price
#             else:
#                 price = product.price

#             for key, value in quantities.items():
#                 if int(key) == product.id:
#                     create_order_item = OrderItem(
#                         order_id=order_id, 
#                         product_id=product_id, 
#                         user=request.user if request.user.is_authenticated else None, 
#                         quantity=value['qty'], 
#                         price=price
#                     )
#                     create_order_item.save()

#         # 3. DELETE THE CART
#         for key in list(request.session.keys()):
#             if key == "session_key":
#                 del request.session[key]

#         messages.success(request, "Order Placed Successfully!")
#         return redirect('payment_success')
        
#     else:
#         messages.error(request, "Access Denied")
#         return redirect('home')
# def orders(request, pk):
#     if request.user.is_authenticated and request.user.is_superuser:
#         # 1. Grab the specific order
#         order = Order.objects.get(id=pk)
        
#         # 2. Grab all the items attached to that specific order
#         items = OrderItem.objects.filter(order=pk)

#         # 3. Handle the form to update Shipping Status
#         if request.method == "POST":
#             status = request.POST.get('shipping_status')
            
#             # Check if they selected Shipped or Un-Shipped
#             if status == "true":
#                 order.shipped = True
#             else:
#                 order.shipped = False
                
#             # Save it! (Your Python signal from models.py will automatically handle the date!)
#             order.save()
#             messages.success(request, "Shipping Status Updated!")
#             return redirect('home')

#         return render(request, 'payment/orders.html', {"order": order, "items": items})
        
#     else:
#         messages.error(request, "Access Denied")
#         return redirect('home')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# ######################################
# Razorpay Integration Code Below
# #####################################
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from cart.cart import Cart
from .forms import ShippingForm
from .models import ShippingAddress, Order, OrderItem

# Initialize the Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_success(request):
    return render(request, 'payment/payment_success.html')

def checkout(request):
    # ==========================================
    # SECURITY CHECK: Block logged-out users
    # ==========================================
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to checkout!")
        return redirect('login')

    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
    shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

    return render(request, 'payment/checkout.html', {
        'cart_products': cart_products,
        'quantities': quantities,
        'totals': totals,
        'shipping_form': shipping_form,
    })

def not_shipped_dash(req):
    if req.user.is_authenticated and req.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if req.method == 'POST':
            num = req.POST.get('num')
            order = Order.objects.get(id=num)
            order.shipped = True
            order.save()
            messages.success(req, 'Order Marked as Shipped!')
            return redirect('not_shipped_dash')
        return render(req, 'payment/not_shipped_dash.html', {'orders': orders})
    else:
        messages.success(req, 'Access Denied')
        return redirect('home')

def shipped_dash(req):
    if req.user.is_authenticated and req.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        return render(req, 'payment/shipped_dash.html', {'orders': orders})
    else:
        messages.success(req, 'Access Denied')
        return redirect('home')

def orders(req, pk):
    if req.user.is_authenticated and req.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        if req.method == 'POST':
            status = req.POST.get('shipping_status')
            order.shipped = True if status == 'true' else False
            order.save()
            messages.success(req, 'Shipping Status Updated!')
            return redirect('home')
        return render(req, 'payment/orders.html', {'order': order, 'items': items})
    else:
        messages.error(req, 'Access Denied')
        return redirect('home')

def my_orders(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your orders.')
        return redirect('login')

    orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
    if not orders.exists():
        messages.info(request, 'You have no past orders yet.')

    return render(request, 'payment/my_orders.html', {'orders': orders})

def billing_info(request):
    # ==========================================
    # SECURITY CHECK: Block logged-out users
    # ==========================================
    if not request.user.is_authenticated:
        messages.error(request, "Access Denied. You must be logged in to proceed to billing.")
        return redirect('login')

    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # ==========================================
        # SAFETY CHECK: Stripe Minimum Amount (₹50)
        # ==========================================
        if float(totals) < 50:
            messages.error(request, "Minimum order amount is ₹50 to process via card. Please add more items to your cart.")
            return redirect('cart_summary')

        # Capture shipping info and save to session safely
        shipping_info = request.POST.dict()
        request.session['my_shipping'] = shipping_info
        request.session.modified = True 
        
        # Stripe requires amounts in cents/paise
        amount_in_cents = int(float(totals) * 100) 
        
        try:
            # Create the Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr', 
                        'unit_amount': amount_in_cents,
                        'product_data': {
                            'name': 'MacStore Order',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('process_order')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('checkout')),
            )
        except Exception as e:
            messages.error(request, str(e))
            return redirect('checkout')
        
        return render(request, "payment/billing_info.html", {
            "cart_products": cart_products, 
            "quantities": quantities, 
            "totals": totals, 
            "shipping_info": shipping_info,
            "stripe_session_id": checkout_session.id,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        })
    else:
        messages.error(request, "Access Denied")
        return redirect('home')

def process_order(request):
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                cart = Cart(request)
                cart_products = cart.get_prods()
                quantities = cart.get_quants()
                totals = cart.cart_total()

                if totals == 0 or not cart_products:
                    messages.warning(request, "Cart was empty. No new order created.")
                    return redirect('home')

                my_shipping = request.session.get('my_shipping', {})
                
                full_name = my_shipping.get('shipping_full_name', '')
                email = my_shipping.get('shipping_email', '')
                shipping_address = f"{my_shipping.get('shipping_address1', '')}\n{my_shipping.get('shipping_address2', '')}\n{my_shipping.get('shipping_city', '')}\n{my_shipping.get('shipping_state', '')}\n{my_shipping.get('shipping_zipcode', '')}\n{my_shipping.get('shipping_country', '')}"
                amount_paid = totals

                if request.user.is_authenticated:
                    create_order = Order(user=request.user, fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
                else:
                    create_order = Order(fullname=full_name, email=email, ShippingAddress=shipping_address, amount_paid=amount_paid)
                
                create_order.save()
                order_id = create_order.pk

                for product in cart_products:
                    price = product.sale_price if product.is_sales else product.price
                    for key, value in quantities.items():
                        if int(key) == product.id:
                            create_order_item = OrderItem(
                                order_id=order_id, 
                                product_id=product.id, 
                                user=request.user if request.user.is_authenticated else None, 
                                quantity=value['qty'], 
                                price=price
                            )
                            create_order_item.save()

                keys_to_delete = ['session_key', 'cart', 'my_shipping']
                for key in keys_to_delete:
                    if key in request.session:
                        del request.session[key]
                
                request.session.modified = True

                if request.user.is_authenticated:
                    try:
                        current_profile = request.user.profile
                        current_profile.old_cart = ""
                        current_profile.save()
                    except Exception:
                        pass

                messages.success(request, "Payment Successful & Order Placed!")
                return redirect('payment_success')
            
            else:
                messages.error(request, "Payment was not completed.")
                return redirect('checkout')
                
        except Exception as e:
            messages.error(request, f"An error occurred during order creation: {str(e)}")
            return redirect('home')
        
    else:
        messages.error(request, "Invalid payment session.")
        return redirect('home')