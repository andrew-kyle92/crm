from datetime import datetime as dt

from crm.models import Task, Client

from django.db.models import Q


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
                return Task.objects.filter(**query_by).order_by(f'-{column}')
            else:
                return Task.objects.filter(**query_by).order_by(column)
        else:
            return Task.objects.filter(**query_by)

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
