# bar/urls.py
from django.urls import path
from .views import CreateCategoryView, AllCategoriesView, AddDrinkView, DrinkListView, CartView, TransactionView, CreateOrderView, CompleteTransactionView, ViewInvoiceView, AllInvoicesView,  AddDrinkQuantityView, ReduceDrinkQuantityView


urlpatterns = [
    path('drinks/', DrinkListView.as_view(), name='drink_list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('transaction/', TransactionView.as_view(), name='transaction'),
    path('create_order/', CreateOrderView.as_view(), name='create-order'),

    path('complete_transaction/', CompleteTransactionView.as_view(), name='complete_transaction'),
    path('view_invoice/<int:invoice_id>/', ViewInvoiceView.as_view(), name='view_invoice'),
    path('view_invoice/<int:invoice_id>/', ViewInvoiceView.as_view(), name='view_invoice'),  # Add this line
    path('all_invoices/', AllInvoicesView.as_view(), name='all_invoices'),  # Add this line for AllInvoicesView
    path('add_drink_quantity/<int:drink_id>/', AddDrinkQuantityView.as_view(), name='add_drink_quantity'),
    path('reduce_drink_quantity/<int:drink_id>/', ReduceDrinkQuantityView.as_view(), name='reduce_drink_quantity'),


    path('create_category/', CreateCategoryView.as_view(), name='create_category'),  # Add this line
    path('add_drink/', AddDrinkView.as_view(), name='add_drink'),  # Add this line
    path('all_categories/', AllCategoriesView.as_view(), name='all_categories'),  # Add this line for AllCategoriesView
    
   
    
    
]