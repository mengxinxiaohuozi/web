from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'loans'

urlpatterns = [
    # 登录相关URL
    path('login/', auth_views.LoginView.as_view(template_name='loans/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 原有URL
    path('', views.index, name='index'),
    path('search/', views.search_loan, name='search'),
    path('upload/', views.upload_template, name='upload'),
    path('download-template/', views.download_template, name='download_template'),
    path('export/', views.export_records, name='export_records'),
    path('manage/', views.manage_records, name='manage'),
    path('edit/<int:record_id>/', views.edit_record, name='edit_record'),
] 