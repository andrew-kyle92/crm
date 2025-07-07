import json
from datetime import date

from django.conf import settings, Settings
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, CreateView, UpdateView

from crm.forms import ActivityForm, LoginForm, CustomerForm, NoteForm, PolicyForm, SettingsForm
from crm.models import Activity, Client, Note, Policy, UserSettings
from crm.utils import *


class IndexView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Home"
    template_name = "crm/index.html"

    def get(self, request):
        all_activities = Activity.objects.all().order_by('-due_date')
        todays_activities = all_activities.filter(due_date__exact=date.today()).order_by('-due_date')
        customers = Client.objects.all()
        context = {
            "title": self.title,
            "user": request.user,
            "activities": all_activities,
            "todays_activities": todays_activities,
            "customers": customers,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
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
        # gtag
        context["gtag"] = settings.GOOGLE_ANALYTICS_TAG,
        # initializing the URLFilters class
        url_filters = URLFilters()
        params = kwargs.get("params", None)
        if params is not None and len(params.keys()) > 0:
            activities = url_filters.get_activities(kwargs.get("params"))
        else:
            activities = Activity.objects.all().order_by('-due_date')
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
    action = "add"

    def get(self, request, customer_pk):
        customer = Client.objects.get(pk=customer_pk)
        form = ActivityForm(initial={"assigned_to": request.user, "client": customer}, customer_instance=customer)
        context = {
            "title": self.title,
            "form": form,
            "customer": customer,
            "action": self.action,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)

    @staticmethod
    def post(request, customer_pk):
        customer = Client.objects.get(pk=customer_pk)
        form = ActivityForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
        return redirect('activities')


class EditActivityView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    template_name = "crm/forms/activity_form.html"
    form_class = ActivityForm
    model = Activity
    action = "edit"

    def get_context_data(self, **kwargs):
        context = super(EditActivityView, self).get_context_data(**kwargs)
        # gtag
        context["gtag"] = settings.GOOGLE_ANALYTICS_TAG,
        context["action"] = self.action
        context["title"] = "Edit Activity"
        context["customer"] = Client.objects.get(pk=self.kwargs.get("customer_pk"))
        return context

    def get_object(self, queryset=None):
        activity_pk = self.kwargs.get("activity_pk")
        obj = get_object_or_404(Activity, pk=activity_pk)
        return obj

    def get_form_kwargs(self):
        kwargs = super(EditActivityView, self).get_form_kwargs()
        self.initial["instance"] = self.get_object()
        kwargs["customer_instance"] = Client.objects.get(pk=self.kwargs.get("customer_pk"))
        return kwargs

    def get_success_url(self):
        return reverse_lazy("activity", kwargs={"pk": self.object.pk})


class ActivityView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    template_name = "crm/activity.html"
    title = ""

    def get(self, request, customer_pk, activity_pk):
        activity = Activity.objects.get(pk=activity_pk)
        self.title = activity.subject[0:50] + " | Activity"
        context = {
            "title": self.title,
            "activity": activity,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
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
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)


class AddCustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Add Customer"
    template_name = 'crm/forms/customer_form.html'
    map_api_key = settings.MAP_API_KEY
    action = "add"

    def get(self, request):
        form = CustomerForm()
        context = {
            "title": self.title,
            "form": form,
            "map_api_key": self.map_api_key,
            "action": self.action,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
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
                "map_api_key": self.map_api_key,
                "action": self.action,
                "gtag": settings.GOOGLE_ANALYTICS_TAG,
            }
            return render(request, self.template_name, context)


class EditCustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = "Edit Customer"
    template_name = 'crm/forms/customer_form.html'
    map_api_key = settings.MAP_API_KEY
    action = "edit"

    def get(self, request, customer_pk, *args, **kwargs):
        customer = Client.objects.get(pk=customer_pk)
        form = CustomerForm(instance=customer)
        context = {
            "title": self.title,
            "form": form,
            "map_api_key": self.map_api_key,
            "action": self.action,
            "customer": customer,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)

    def post(self, request, customer_pk, *args, **kwargs):
        customer = Client.objects.get(pk=customer_pk)
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('customer', kwargs={'pk': customer_pk}))
        else:
            context = {
                "form": form,
                "title": self.title,
                "map_api_key": self.map_api_key,
                "action": self.action,
                "customer": customer,
                "gtag": settings.GOOGLE_ANALYTICS_TAG,
            }
            return render(request, self.template_name, context)


class CustomerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    title = " | Customers"
    template_name = 'crm/customer_details.html'

    def get(self, request, customer_pk, *args, **kwargs):
        customer = Client.objects.get(pk=customer_pk)
        self.title = customer.__str__() + self.title
        context = {
            "title": self.title,
            "customer": customer,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)


class AddNoteView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("crm")
    title = "Add Note"
    template_name = 'crm/forms/notes_form.html'

    def get(self, request, pk, *args, **kwargs):
        task = Activity.objects.get(pk=pk)
        form = NoteForm(initial={"assigned_to": request.user, "task": task})
        context = {
            "title": self.title,
            "form": form,
            "activity": task,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('task', kwargs={'pk': pk}))
        else:
            activity = Activity.objects.get(pk=form.cleaned_data["task"].pk)
            context = {
                "form": form,
                "title": self.title,
                "activity": activity,
                "gtag": settings.GOOGLE_ANALYTICS_TAG,
            }
            return render(request, self.template_name, context)


class AddPolicyView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("crm")
    template_name = "crm/forms/add_policy.html"
    form_class = PolicyForm
    model = Policy
    title = "Add Policy"
    action = "add"
    initial = {}

    def get_context_data(self, **kwargs):
        context = super(AddPolicyView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["action"] = self.action
        context["customer"] = Client.objects.get(pk=self.kwargs["customer_pk"])
        # gtag
        context["gtag"] = settings.GOOGLE_ANALYTICS_TAG,
        return context

    def get(self, request, *args, **kwargs):
        kwargs["customer_pk"] = kwargs.get("customer_pk")
        return super(AddPolicyView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddPolicyView, self).get_form_kwargs()
        kwargs["initial"]["client"] = Client.objects.get(pk=self.kwargs["customer_pk"])
        return kwargs


class SettingsView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")
    template_name = "crm/settings.html"
    title = "Settings"

    def get(self, request, *args, **kwargs):
        user = request.user
        user_settings = UserSettings.objects.get(user=user)
        context = {
            "settings": user_settings,
            "title": self.title,
            "gtag": settings.GOOGLE_ANALYTICS_TAG,
        }
        return render(request, self.template_name, context)


class EditSettingsView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy("login")
    title = "Edit Settings"
    template_name = "crm/forms/settings_form.html"
    form_class = SettingsForm
    model = UserSettings

    def get_context_data(self, **kwargs):
        context = super(EditSettingsView, self).get_context_data(**kwargs)
        context["title"] = self.title
        # gtag
        context["gtag"] = settings.GOOGLE_ANALYTICS_TAG,

        return context

    def get_success_url(self):
        return reverse_lazy("settings", kwargs={"pk": self.request.user.pk})


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
        # gtag
        context["gtag"] = settings.GOOGLE_ANALYTICS_TAG,
        return context


def user_logout(request):
    logout(request)
    return redirect("index")
