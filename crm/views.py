import json
from datetime import date

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView

from .forms import TaskForm, LoginForm, CustomerForm, NoteForm
from .models import Task, Client, Note
from .utils import *


class IndexView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Home"
    template_name = "crm/index.html"

    def get(self, request):
        all_activities = Task.objects.filter(assigned_to=request.user).order_by('-due_date')
        todays_activities = all_activities.filter(due_date__exact=date.today(), assigned_to=request.user).order_by('-due_date')
        customers = Client.objects.all()
        context = {
            "title": self.title,
            "user": request.user,
            "activities": all_activities,
            "todays_activities": todays_activities,
            "customers": customers,
        }
        return render(request, self.template_name, context)


class ActivitiesView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Activities"
    template_name = "crm/activities.html"

    def get_context_data(self, **kwargs):
        context = super(ActivitiesView, self).get_context_data(**kwargs)
        context["title"] = self.title
        # initializing the URLFilters class
        url_filters = URLFilters()
        params = kwargs.get("params", None)
        if params is not None and len(params.keys()) > 0:
            activities = url_filters.get_activities(kwargs.get("params"))
        else:
            activities = Task.objects.all().order_by('-due_date')
        paginator = Paginator(activities, 10)
        context["paginator"] = paginator
        context["page"] = paginator.get_page(kwargs.get("page"))

        return context

    def get(self, request, *args, **kwargs):
        # getting all URL parameters
        params = {
            "params": {
                "column": request.GET.get("column", None),
                "direction": request.GET.get("direction", None),
                "filter": request.GET.get("filter", None),
                "page": request.GET.get("page", None),
            }
        }
        for key, value in params.items():
            if value is None:
                params.pop(key)

        kwargs.update(**params)

        return super(ActivitiesView, self).get(request, **kwargs)


class AddActivityView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Add Activity"
    template_name = "crm/forms/activity_form.html"

    def get(self, request):
        customer_id = request.GET.get("pk", None)
        if customer_id:
            customer = Client.objects.get(pk=customer_id)
            form = TaskForm(initial={"assigned_to": request.user, "client": customer})
        else:
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
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    template_name = "crm/activity.html"
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
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
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
    redirect_field_name = "next"
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
    redirect_field_name = "next"
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
        else:
            context = {
                "form": form,
                "title": self.title,
            }
            return render(request, self.template_name, context)


class CustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
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


class AddNoteView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("crm")
    title = "Add Note"
    template_name = 'crm/forms/notes_form.html'

    def get(self, request, pk, *args, **kwargs):
        task = Task.objects.get(pk=pk)
        form = NoteForm(initial={"assigned_to": request.user, "task": task})
        context = {
            "title": self.title,
            "form": form,
            "activity": task,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('task', kwargs={'pk': pk}))
        else:
            context = {
                "form": form,
                "title": self.title,
            }
            return render(request, self.template_name, context)


# ########## Authentication Views ##########
class UserLoginView(LoginView):
    template_name = "crm/login.html"
    title = "Login"
    form_class = LoginForm
    success_url = reverse_lazy("index")
    redirect_authenticated_user = True

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(UserLoginView, self).dispatch(request, *args, **kwargs)

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
        activity_notes = Note.objects.filter(task=activity)
        activity_html = render_to_string(
            "crm/activity.html",
            {
                "activity": activity,
                "activity_notes": activity_notes,
            }
        )
        context = {
            "status": "success",
            "activity": activity_html,
        }
        return JsonResponse(context, safe=False)
    except Task.DoesNotExist:
        context = {
            "status": "error",
            "message": "No activity found",
        }
        return JsonResponse(json.dumps(context), safe=False)


def fetch_users(request):
    user_query = request.GET.get("q", None)
    if user_query is not None:
        users = get_users_list(user_query)
        return JsonResponse(users, safe=False)
    else:
        return JsonResponse({"status": "error", "message": "No users found"}, Safe=True)


def fetch_modal_data(request):
    modal_type = request.GET.get("type", None)
    if modal_type is not None:
        if modal_type == "note":
            activity_id = request.GET.get("activityId", None)
            activity = Task.objects.get(pk=activity_id)
            template = "crm/forms/notes_form.html"
            form = NoteForm(initial={"assigned_to": request.user, "task": activity})
            form_context = {
                "activity": activity,
                "form": form,
            }
            modal_body_html = render_to_string(template, form_context)
            res_context = {
                "status": "success",
                "html": modal_body_html,
            }
            return JsonResponse(res_context, safe=False)
        else:
            return JsonResponse({"status": "error", "message": "No modal found"}, safe=False)
    else:
        return JsonResponse({"status": "error", "message": "No modal found"}, safe=False)


def fetch_submit_form(request):
    form = NoteForm(request.POST)
    if form.is_valid():
        instance = form.save()
        print(instance)
        return JsonResponse({"formData": instance.__dict__}, safe=False)
    else:
        return JsonResponse({"formData": form.errors}, safe=False)
