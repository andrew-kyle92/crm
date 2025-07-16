from .views import (
    IndexView, ActivitiesView, AddActivityView, ActivityView, CustomersView, AddCustomerView,
    EditCustomerView, CustomerView, AddNoteView, AddPolicyView, ViewPolicyView, EditPolicyView, UserLoginView, logout
)

from .fetch_views import (
    fetch_activity, fetch_users, fetch_modal_data, fetch_submit_form, fetch_mark_complete
)
