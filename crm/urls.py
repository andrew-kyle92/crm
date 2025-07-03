from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from crm.views import *
from crm.views.views import AddPolicyView, EditActivityView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('activities/', ActivitiesView.as_view(), name='activities'),
    path('activities/new-activity/', AddActivityView.as_view(), name='new-activity'),
    path('activities/activity/<int:pk>/', ActivityView.as_view(), name='activity'),
    path('activities/activity/<int:pk>/edit/', EditActivityView.as_view(), name='edit-activity'),
    path('activities/activity/<int:pk>/add-note/', AddNoteView.as_view(), name='add-note'),
    path('customers/', CustomersView.as_view(), name='customers'),
    path('customers/view/<int:pk>/', CustomerView.as_view(), name='customer'),
    path('customers/add/', AddCustomerView.as_view(), name='add-customer'),
    path('customers/edit/<int:pk>/', EditCustomerView.as_view(), name='edit-customer'),
    path("customers/view/<int:pk>/policy/add/", AddPolicyView.as_view(), name="add-policy"),
    # authentication_views
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    # fetch requests
    path('fetch-activity/', fetch_activity, name='fetch-activity'),
    path('fetch-users/', fetch_users, name='fetch-users'),
    path('fetch-modal-data/', fetch_modal_data, name='fetch-modal-data'),
    path('fetch-submit-form/', fetch_submit_form, name='fetch-submit-form'),
    path('fetch-mark-complete/', fetch_mark_complete, name='fetch-mark-complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
