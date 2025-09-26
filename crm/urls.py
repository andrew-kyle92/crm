from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from crm.views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('activities/', ActivitiesView.as_view(), name='activities'),
    path('customers/', CustomersView.as_view(), name='customers'),
    path('customers/view/<int:customer_pk>/', CustomerView.as_view(), name='customer'),
    path('customers/add/', AddCustomerView.as_view(), name='add-customer'),
    path('customers/edit/<int:customer_pk>/', EditCustomerView.as_view(), name='edit-customer'),
    path("customers/view/<int:customer_pk>/policy/add/", AddPolicyView.as_view(), name="add-policy"),
    path("customers/view/<int:customer_pk>/policy/view/<int:policy_pk>/", ViewPolicyView.as_view(), name="view-policy"),
    path("customers/view/<int:customer_pk>/policy/edit/<int:policy_pk>/", EditPolicyView.as_view(), name="edit-policy"),
    path('customers/view/<int:customer_pk>/activity/<int:activity_pk>/', ActivityView.as_view(), name='activity'),
    path("customers/view/<int:customer_pk>/activity/add/", AddActivityView.as_view(), name="new-activity"),
    path("customers/view/<int:customer_pk>/activity/<int:activity_pk>/edit/", EditActivityView.as_view(), name="edit-activity"),
    path("customers/view/<int:customer_pk>/activity/<int:activity_pk>/add-note/", EditActivityView.as_view(), name="add-note"),
    path("profile/<int:pk>/", views.SettingsView.as_view(), name="settings"),
    path("profile/<int:pk>/edit/", views.EditSettingsView.as_view(), name="edit-settings"),
    path("households/add/", AddHouseholdView.as_view(), name="add-household"),
    path("households/edit/<int:household_pk>", EditHouseholdView.as_view(), name="edit-household"),
    path("households/view/<int:household_pk>/", ViewHouseholdView.as_view(), name="view-household"),
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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
