import json

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View

from .forms import TaskForm, LoginForm, CustomerForm
from .models import Task, Client


class IndexView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = "Home"
    template_name = "crm/index.html"

    def get(self, request):
        context = {
            "title": self.title,
            "user": request.user
        }
        return render(request, self.template_name, context)


class ActivitiesView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = "Activities"
    template_name = "crm/activities.html"

    def get(self, request):
        context = {
            "title": self.title,
            "user": request.user
        }

        return render(request, self.template_name, context)


class AddActivityView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = "Add Activity"
    template_name = "crm/forms/activity_form.html"

    def get(self, request):
        form = TaskForm(initial={"assigned_to": request.user})
        context = {
            "title": self.title,
            "form": form,
        }
        return render(request, self.template_name, context)

    @staticmethod
    def post(request):
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('activities')


class ActivityView(LoginRequiredMixin, View):
    template_name = "crm/activity.html"
    login_url = reverse_lazy("login")
    title = ""

    def get(self, request, pk):
        activity = Task.objects.get(pk=pk)
        self.title = activity.subject[0:50] + " | Activity"
        context = {
            "title": self.title,
            "activity": activity,
        }
        return render(request, self.template_name, context)


class CustomersView(LoginRequiredMixin, View):
    title = "Customers"
    template_name = 'crm/customers.html'

    def get(self, request, *args, **kwargs):
        customers = Client.objects.all()
        context = {
            "title": self.title,
            "customers": customers,
        }
        return render(request, self.template_name, context)


class AddCustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = "Add Customer"
    template_name = 'crm/forms/customer_form.html'

    def get(self, request):
        form = CustomerForm()
        context = {
            "title": self.title,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('customers')
        else:
            context = {
                "form": form,
                "title": self.title,
            }
            return render(request, self.template_name, context)


class EditCustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = "Edit Customer"
    template_name = 'crm/forms/customer_form.html'
    map_api_key = settings.MAP_API_KEY

    def get(self, request, pk, *args, **kwargs):
        customer = Client.objects.get(pk=pk)
        form = CustomerForm(instance=customer)
        context = {
            "title": self.title,
            "form": form,
            "map_api_key": self.map_api_key
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        customer = Client.objects.get(pk=pk)
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('customer', kwargs={'pk': pk}))


class CustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    title = " | Customers"
    template_name = 'crm/customer_details.html'

    def get(self, request, pk, *args, **kwargs):
        customer = Client.objects.get(pk=pk)
        self.title = customer.__str__() + self.title
        context = {
            "title": self.title,
            "customer": customer,
        }
        return render(request, self.template_name, context)


# ########## Authentication Views ##########
class UserLoginView(LoginView):
    template_name = "crm/login.html"
    title = "Login"
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(UserLoginView, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context


def user_logout(request):
    logout(request)
    return redirect("index")


# ********** Fetch requests **********
def fetch_activity(request):
    try:
        # getting the activity ID from the payload
        activity_id = request.GET.get("activity_id", None)
        if not activity_id:
            raise Exception("No activity id")
        activity = Task.objects.get(pk=activity_id)  # getting the activity
        activity_html = render_to_string("crm/activity.html", {"activity": activity})
        context = {
            "status": "success",
            "activity": activity_html,
        }
        return JsonResponse(context, safe=True)
    except Task.DoesNotExist:
        context = {
            "status": "error",
            "message": "No activity found",
        }
        return JsonResponse(json.dumps(context), safe=False)
