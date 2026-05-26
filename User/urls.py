from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='User/login.html'), name='login'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # URLS MPYA ZA CRUD YA ADMIN
    path('admin-dashboard/', views.AdminLoanListView.as_view(), name='admin_loan_list'),
    path('admin-dashboard/loan/<int:pk>/', views.AdminLoanDetailView.as_view(), name='admin_loan_detail'),
    path('admin-dashboard/loan/new/', views.AdminLoanCreateView.as_view(), name='admin_loan_create'),
    path('admin-dashboard/loan/<int:pk>/edit/', views.AdminLoanUpdateView.as_view(), name='admin_loan_update'),
    path('admin-dashboard/loan/<int:pk>/delete/', views.AdminLoanDeleteView.as_view(), name='admin_loan_delete'),
]