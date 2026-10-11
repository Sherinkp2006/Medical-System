from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # Authentication
    path('', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # List all medicines
    path('list-medicine', views.list_medicines, name='medicine_list'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/<int:pk>/delete/', views.delete_user, name='user_delete'),

    # Add a new medicine
    path('add/', views.add_medicine, name='medicine_add'),

    # Edit an existing medicine (by primary key)
    path('edit/<int:pk>/', views.edit_medicine, name='medicine_edit'),

    # Sell a medicine
    path('sell/<int:pk>/', views.medicine_sell, name='medicine_sell'),

    # Delete a medicine
    path('delete/<int:pk>/', views.delete_medicine, name='medicine_delete'),
]