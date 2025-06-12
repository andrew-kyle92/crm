from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('activity/<int:pk>/', views.ActivityView.as_view(), name='activity'),
    path('activities/', views.ActivitiesView.as_view(), name='activities'),
    path('new-activity/', views.AddActivityView.as_view(), name='new-activity'),
    path('customers/', views.CustomersView.as_view(), name='customers'),
    path('customers/view/<int:pk>/', views.CustomerView.as_view(), name='customer'),
    path('customers/add/', views.AddCustomerView.as_view(), name='add-customer'),
    path('customers/edit/<int:pk>/', views.EditCustomerView.as_view(), name='edit-customer'),
    # authentication_views
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    # fetch requests
    path('fetch-activity/', views.fetch_activity, name='fetch-activity'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
