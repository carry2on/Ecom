from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session
        # Get request so we can check if the user is logged in
        self.request = request

        cart = self.session.get('session_key')

        if cart is None:
            cart = self.session['session_key'] = {}

        # UPGRADED ROBUST CART DATA FIX
        for product_id, item in cart.items():
            if type(item) is int:
                cart[product_id] = {'qty': item}
            elif type(item) is dict and 'qty' not in item:
                item['qty'] = 1

        self.cart = cart


    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = int(quantity)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'price': str(product.price),
                'qty': product_qty
            }
        else:
            self.cart[product_id]['qty'] += product_qty

        self.session['session_key'] = self.cart
        self.session.modified = True

        # NEW: SAVE CART TO DATABASE
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Convert dictionary to string and replace single quotes with double quotes for JSON parsing
            carty = str(self.cart).replace("\'", "\"")
            # Save it to the profile
            current_user.update(old_cart=str(carty))
        

    def __len__(self):
        return sum(int(item.get('qty', 0)) for item in self.cart.values())
    

    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        if product_id in self.cart:
            self.cart[product_id]['qty'] = product_qty

        self.session['session_key'] = self.cart
        self.session.modified = True

        # NEW: SAVE CART TO DATABASE
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart).replace("\'", "\"")
            current_user.update(old_cart=str(carty))

        return self.cart
    
    def delete(self, product):
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]

        self.session['session_key'] = self.cart
        self.session.modified = True

        # NEW: SAVE CART TO DATABASE
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart).replace("\'", "\"")
            current_user.update(old_cart=str(carty))

        return self.cart
    
    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0
        
        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sales:
                        total = total + (product.sale_price * int(value['qty']))
                    else:
                        total = total + (product.price * int(value['qty']))

        return total