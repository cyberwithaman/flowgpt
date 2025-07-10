"""
URL configuration for flowgpt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from flowgptapp import views
from flowgptapp.dashboard import AdminDashboardView

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('pipeline/<int:pipeline_id>/', views.pipeline_detail, name='pipeline_detail'),
    path('executions/', views.execution_history, name='execution_history'),
    path('execution/<int:execution_id>/', views.execution_detail, name='execution_detail'),
    path('contact/', views.contact, name='contact'),
    path('api/execute/', views.execute_pipeline_view, name='execute_pipeline'),
    path('api/execution/<int:execution_id>/status/', views.get_execution_status, name='execution_status'),
]

# Customize admin site
admin.site.site_header = 'FlowGPT Admin'
admin.site.site_title = 'FlowGPT Admin Portal'
admin.site.index_title = 'FlowGPT Administration'
