# ********** Fetch requests **********
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from crm.models import *
from crm.utils import *
from crm.forms import NoteForm

import json

from crm.utils.view_methods import ModalContextBuilder


def fetch_activity(request):
    try:
        # getting the activity ID from the payload
        activity_id = request.GET.get("activity_id", None)
        if not activity_id:
            raise Exception("No activity id")
        activity = Activity.objects.get(pk=activity_id)  # getting the activity
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
    except Activity.DoesNotExist:
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
    mcb = ModalContextBuilder()
    if modal_type is not None:
        modal_body_html = mcb.get_modal_content(request.GET, user=request.user)
        res_context = {
            "status": "success",
            "html": modal_body_html,
        }
        return JsonResponse(res_context, safe=False)
    else:
        return JsonResponse({"status": "error", "message": "No modal found"}, safe=False)


def fetch_submit_form(request):
    post_data = request.POST.copy()
    form_class = get_form_class(post_data.pop("form_class")[0])
    if "instance_id" in post_data:
        instance = Note.objects.get(pk=post_data.pop("instance_id")[0])
    else:
        instance = None
    form = form_class(request.POST, instance=instance)
    if form.is_valid():
        instance = form.save()
        context = {"status": "success"}
        if form_class.__name__ == "NoteForm":
            instance_dict = instance.__dict__
            instance_dict.pop("_state")
            instance_dict["formatted_date"] = instance.get_formatted_date()
            context["instance"] = instance_dict
        else:
            context["successUrl"] = reverse_lazy("view-household", kwargs={"household_pk": instance.pk})

        return JsonResponse(context, safe=False)
    else:
        context = {"form": form}
        if form_class.__name__ == "NoteForm":
            activity = Activity.objects.get(pk=form.cleaned_data["activity"].pk)
            context["activity"] = activity
            template = "crm/forms/notes_form.html"
        else:
            template = "crm/forms/household_form.html"

        html = render_to_string(template, context)
        context = {
            "status": "error",
            "html": html,
        }
        return JsonResponse(context, safe=False)


def fetch_mark_complete(request):
    activity_id = request.GET.get("activityId", None)
    if activity_id is not None:
        try:
            activity = Activity.objects.get(pk=activity_id)
            activity.status = "completed"
            activity.save()
            return JsonResponse({"status": "success"}, safe=False)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, safe=False)
    else:
        return JsonResponse({"status": "error", "message": "No activity found"}, safe=False)
