from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from .forms import TaskForm, LoginForm


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


class UserLoginView(LoginView):
    template_name = "crm/login.html"
    form_class = LoginForm
    pass


def user_logout(request):
    logout(request)
    return redirect("index")
