# bar/views.py
from django.shortcuts import render, redirect
from django.views import View
from .models import Category, Drink, Order, Transaction, Invoice


class AllCategoriesView(View):
    template_name = 'all_categories.html'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

class CreateCategoryView(View):
    template_name = 'create_category.html'

    def post(self, request):
        category_name = request.POST.get('category_name')
        category = Category.objects.create(name=category_name)
        return redirect('drink_list')

    def get(self, request):
        return render(request, self.template_name)

class AddDrinkView(View):
    template_name = 'add_drink.html'

    def post(self, request):
        drink_name = request.POST.get('drink_name')
        drink_price = float(request.POST.get('drink_price', 0))
        drink_quantity = int(request.POST.get('drink_quantity', 0))
        category_id = int(request.POST.get('drink_category'))

        category = Category.objects.get(pk=category_id)

        drink = Drink.objects.create(
            name=drink_name,
            price=drink_price,
            quantity_in_stock=drink_quantity,
            category=category
        )
        return redirect('drink_list')

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

class DrinkListView(View):
    template_name = 'drink_list.html'

    def get(self, request):
        drinks = Drink.objects.all()
        return render(request, self.template_name, {'drinks': drinks})
    
class CreateOrderView(View):
    template_name = 'create_order.html'

    def get(self, request):
        drinks = Drink.objects.all()
        return render(request, self.template_name, {'drinks': drinks})

    def post(self, request):
        drink_id = request.POST.get('drink_id')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity not provided
        drink = Drink.objects.get(pk=drink_id)
        total_price = drink.price * quantity  # Calculate the total price
        order = Order.objects.create(drink=drink, quantity=quantity, total_price=total_price)  # Set the total price
        
        # Add the drink ID to the cart session variable
        cart_items = request.session.get('cart', [])
        cart_items.append(drink.pk)
        request.session['cart'] = cart_items

        return redirect('cart')
    


class AddDrinkQuantityView(View):
    template_name = 'add_drink_quantity.html'

    def post(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        quantity_to_add = int(request.POST.get('quantity_to_add', 0))
        if quantity_to_add > 0:
            drink.quantity_in_stock += quantity_to_add
            drink.save()
        return redirect('drink_list')

    def get(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        return render(request, self.template_name, {'drink': drink})

class ReduceDrinkQuantityView(View):
    template_name = 'reduce_drink_quantity.html'

    def post(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        quantity_to_reduce = int(request.POST.get('quantity_to_reduce', 0))
        if quantity_to_reduce > 0:
            drink.quantity_in_stock -= quantity_to_reduce
            drink.save()
        return redirect('drink_list')

    def get(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        return render(request, self.template_name, {'drink': drink})
    


class CartView(View):
    template_name = 'cart.html'

    def get(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])
        drinks = Drink.objects.filter(pk__in=cart_items)

        # Calculate drink_quantity for each drink in the cart
        drink_quantities = {}
        for drink in drinks:
            drink_quantity = cart_items.count(drink.pk)
            drink_quantities[drink.pk] = drink_quantity
        return render(request, self.template_name, {'drinks': drinks, 'drink_quantities': drink_quantities})


    def post(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])

        # Get the drink ID to remove from the cart
        drink_id_to_remove = request.POST.get('drink_id_to_remove')

        if drink_id_to_remove:
            try:
                drink_id_to_remove = int(drink_id_to_remove)
                if drink_id_to_remove in cart_items:
                    cart_items.remove(drink_id_to_remove)
                    request.session['cart'] = cart_items
            except ValueError:
                pass  # Ignore if the drink_id_to_remove is not a valid integer

        return redirect('cart')
    

class CompleteTransactionView(View):
    template_name = 'complete_transaction.html'

    def post(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])
        drink_quantities = {}
        for drink_id in cart_items:
            drink_quantity = cart_items.count(drink_id)
            drink_quantities[drink_id] = drink_quantity

        # Check if there is sufficient quantity for each drink in the cart
        insufficient_drinks = []
        for drink_id, quantity in drink_quantities.items():
            drink = Drink.objects.get(pk=drink_id)
            if quantity > drink.quantity_in_stock:
                insufficient_drinks.append(drink)

        if insufficient_drinks:
            return render(request, self.template_name, {'insufficient_drinks': insufficient_drinks})

        # Calculate the total price of the transaction
        total_price = 0
        for drink_id, quantity in drink_quantities.items():
            drink = Drink.objects.get(pk=drink_id)
            total_price += drink.price * quantity

        # Create a new transaction
        transaction = Transaction.objects.create(total_amount=total_price)

        # Create orders and associate with the transaction
        for drink_id, quantity in drink_quantities.items():
            drink = Drink.objects.get(pk=drink_id)
            order = Order.objects.create(drink=drink, quantity=quantity, total_price=drink.price * quantity)
            transaction.orders.add(order)

            # Deduct the ordered quantity from the available quantity for each drink
            drink.quantity_in_stock -= quantity
            drink.save()

        # Create an invoice for the transaction
        invoice = Invoice.objects.create(transaction=transaction)

        # Clear the cart after completing the transaction
        request.session['cart'] = []

        # Redirect to the view_invoice page with the invoice ID
        return redirect('view_invoice', invoice_id=invoice.pk)

    def get(self, request):
        return redirect('cart')  # Redirect to cart if accessing the view via GET







class ViewInvoiceView(View):
    template_name = 'view_invoice.html'

    def get(self, request, invoice_id):
        invoice = Invoice.objects.get(pk=invoice_id)
        return render(request, self.template_name, {'invoice': invoice})
    

class AllInvoicesView(View):
    template_name = 'all_invoices.html'

    def get(self, request):
        invoices = Invoice.objects.all()
        return render(request, self.template_name, {'invoices': invoices})



class TransactionView(View):
    def post(self, request):
        # Get cart items from the session
        cart_items = request.session.get('cart', [])
        drinks = Drink.objects.filter(pk__in=cart_items)

        # Create the order and calculate the total amount
        total_amount = 0
        orders = []
        for drink in drinks:
            quantity = cart_items.count(drink.pk)
            total_price = drink.price * quantity
            order = Order(drink=drink, quantity=quantity, total_price=total_price)
            orders.append(order)
            total_amount += total_price
            # Update the drink's quantity_in_stock
            drink.quantity_in_stock -= quantity
            drink.save()

        # Create a transaction and save it to the database
        transaction = Transaction(total_amount=total_amount)
        transaction.save()
        transaction.orders.set(orders)

        # Clear the cart
        request.session['cart'] = []

        # Generate an invoice for the transaction (optional)

        return render(request, 'transaction_complete.html', {'transaction': transaction})

