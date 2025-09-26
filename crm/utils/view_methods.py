from datetime import datetime as dt

from django.template.loader import render_to_string

from crm.forms import NoteForm, HouseholdForm
from crm.models import *

from django.db.models import Q
from django.apps import apps


def get_users_list(query):
    users = []
    users_queried = Client.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )
    if len(users_queried) > 0:
        for user in users_queried:
            users.append({
                'id': user.id,
                'firstName': user.first_name,
                'lastName': user.last_name,
            })
        return users
    else:
        return False


class ModalContextBuilder:
    def get_modal_content(self, data, **kwargs):
        """
        Takes a query dictionary and gets the form html data relevant to the type.
        Returns a context dictionary.
        """

        # setting the correct modal content type
        modal_content = self.get_model_context_type(data.get("type"))

        # getting kwargs
        for kwarg in modal_content["kwargsList"]:
            try:
                # trying the initial query dict first
                if data.get(kwarg, None) is not None:
                    modal_content["vars"][kwarg] = data.get(kwarg, None)
                elif kwargs.get(kwarg, None) is not None:
                    # trying the kwargs
                    modal_content["vars"][kwarg] = kwargs.get(kwarg, None)
                else:
                    modal_content["vars"][kwarg] = None
            except KeyError:
                return Exception(f"{kwarg} is not a valid kwarg")

        # prepping the form
        form_kwargs = {}
        form = None
        # getting the kwargs for the form
        if data.get("type") == "note":
            instance = Activity.objects.get(pk=modal_content["vars"]["activityId"])
            form_kwargs["initial"] = {"user": modal_content["vars"]["user"], "activity": instance}
            # initializing the form
            form = NoteForm(**form_kwargs)
        elif data.get("type") == "editNote":
            instance = Note.objects.get(pk=modal_content["vars"]["instanceId"])
            form_kwargs["instance"] = instance
            # initializing the form
            form = NoteForm(**form_kwargs)
        elif data.get("type") == "household":
            client_instance = Client.objects.get(pk=modal_content["vars"]["clientId"])
            form_kwargs["initial"] = {"name": client_instance.last_name, "members": [client_instance], "head_of_household": client_instance}
            form = HouseholdForm(**form_kwargs)

        # prepping the template context
        if data.get("type") == "note" or data.get("type") == "editNote":
            activity = Activity.objects.get(pk=modal_content["vars"]["activityId"])
            modal_content["template_context"]["activity"] = activity
        elif data.get("type") == "household" or data.get("type") == "editHousehold":
            modal_content["template_context"]["customers"] = Client.objects.all()

        modal_content["template_context"]["form"] = form

        html = render_to_string(template_name=modal_content["template"], context=modal_content["template_context"])
        return html

    @staticmethod
    def get_model_context_type(content_type):
        modal_content_types = {
            'note': {
                "template": "crm/forms/notes_form.html",
                "kwargsList": ["user", "activityId"],
                "template_context": {"activity": None, "form": None},
                "vars": {},
            },
            'editNote': {
                "template": "crm/forms/notes_form.html",
                "kwargsList": ["user", "activityId", "instanceId"],
                "template_context": {"activity": None, "form": None},
                "vars": {},
            },
            'household': {
                "template": "crm/forms/household_form.html",
                "kwargsList": ["clientId"],
                "template_context": {"client": None, "form": None},
                "vars": {},
            },
        }

        return modal_content_types[content_type]

    @staticmethod
    def get_model(model_name):
        try:
            return apps.get_model("crm", model_name)
        except LookupError:
            return None


class URLFilters:
    def get_activities(self, params):
        # assigning param vars
        filter_type = params.get('filter', None)
        direction = params.get('direction', None)
        column = params.get('column', None)
        # creating a dictionary to query by
        query_by = {}

        # getting filter_type and adding it to the query_by dict
        filter_dict = self.get_filter_param(filter_type)
        if filter_dict is not False:
            query_by.update(filter_dict)

        if direction is not None:
            # checking the direction
            if params.get("") == 'desc':
                return Activity.objects.filter(**query_by).order_by(f'-{column}')
            else:
                return Activity.objects.filter(**query_by).order_by(column)
        else:
            return Activity.objects.filter(**query_by)

    @staticmethod
    def get_filter_param(filter_type):
        filter_dict = {}
        if filter_type == '' or filter_type is None:
            return False
        elif filter_type == 'today':
            filter_dict["due_date__exact"] = dt.now()
        elif filter_type == 'progress':
            filter_dict["status__exact"] = "in_progress"
        elif filter_type == 'completed':
            filter_dict["status__exact"] = "completed"

        return filter_dict


def get_form_class(form_class):
    if form_class == "NoteForm":
        return NoteForm
    elif form_class == "HouseholdForm":
        return HouseholdForm
    else:
        return None
