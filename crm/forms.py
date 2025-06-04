from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crm.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': 'readonly'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # 'description': ProseEditorFormField(sanitize=True),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'subject': 'Subject',
            'description': 'Description',
            'assigned_to': 'Assigned to',
            'priority': 'Priority',
            'status': 'Status',
            'client': 'Customer',
            'policy': 'Policy',
            'activity_type': 'Activity Type',
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        self.fieldsets = [
            {
                "name": "Task Details",
                "fields": [
                    ["subject", "assigned_to"], ["client", "due_date"], "description",
                ],
            },
            {
                "name": "Additional Information",
                "fields": [
                    ["priority", "status"], "activity_type"
                ],
            }
        ]

    def iter_fieldsets(self):
        for fieldset in self.fieldsets:
            f = {"name": fieldset["name"], "fields": []}
            for field in fieldset["fields"]:
                if type(field) is list:
                    fields = []
                    for subfield in field:
                        fields.append(self[subfield])
                    f["fields"].append(fields)
                else:
                    f["fields"].append(self[field])

            yield f


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
