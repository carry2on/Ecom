from django.shortcuts import render

def cart_summary(request):
    return render(request, 'cart_summary.html')

def cart_add(request):
    pass
    # return render(request, 'cart_add.html')

def cart_delete(request):
    pass
    # return render(request, 'cart_delete.html')

def cart_update(request):
    pass
    # return render(request, 'cart_update.html')