from django.shortcuts import render
from .cart import Cart
from django.shortcuts import get_object_or_404
from store.models import  Product
from django.http import JsonResponse

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()   # call the function
    return render(request, 'cart_summary.html', {'cart_products': cart_products})

def cart_add(request):
    # Get the cart
    cart = Cart(request)

    # Test for POST
    if request.POST.get('action') == 'post':

        # Get product ID
        product_id = int(request.POST.get('product_id'))
        product_qty=int(request.POST.get('product_qty'))
        # Lookup product in database
        product = get_object_or_404(Product, id=product_id)

        # Save to session
        cart.add(product=product,quantity=product_qty)
        cart_quantity=cart.__len__()
        # Return response
        # response = JsonResponse({'Product Name': product.name})
        response = JsonResponse({'qty': cart_quantity})
        return response
def cart_delete(request):
    pass
    # return render(request, 'cart_delete.html')

def cart_update(request):
    pass
    # return render(request, 'cart_update.html')