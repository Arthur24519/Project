from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='add_client'),
    path('clients/edit/<int:pk>/', views.ClientUpdateView.as_view(), name='edit_client'),
    path('clients/delete/<int:pk>/', views.ClientDeleteView.as_view(), name='delete_client'),

    path('cars/', views.CarListView.as_view(), name='car_list'), 
    path('cars/add/', views.CarCreateView.as_view(), name='add_car'),  
    path('cars/edit/<int:pk>/', views.CarUpdateView.as_view(), name='edit_car'), 
    path('cars/delete/<int:pk>/', views.CarDeleteView.as_view(), name='delete_car'),

    path('contracts/', views.ContractListView.as_view(), name='contract_list'),
    path('contracts/add/', views.ContractCreateView.as_view(), name='add_contract'),
    path('contracts/edit/<int:pk>/', views.ContractUpdateView.as_view(), name='edit_contract'),
    path('contracts/delete/<int:pk>/', views.ContractDeleteView.as_view(), name='delete_contract'),

    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='add_service'),
    path('services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='edit_service'),
    path('services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='delete_service'),

    path('spareparts/', views.SparePartListView.as_view(), name='sparepart_list'),
    path('spareparts/add/', views.SparePartCreateView.as_view(), name='add_sparepart'),
    path('spareparts/edit/<int:pk>/', views.SparePartUpdateView.as_view(), name='edit_sparepart'),
    path('spareparts/delete/<int:pk>/', views.SparePartDeleteView.as_view(), name='delete_sparepart'),

    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/add/', views.OrderCreateView.as_view(), name='add_order'),
    path('orders/edit/<int:pk>/', views.OrderUpdateView.as_view(), name='edit_order'),
    path('orders/delete/<int:pk>/', views.OrderDeleteView.as_view(), name='delete_order'),

    path('accounts/register/', views.register, name='register'), 
]