from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crm.models import Activity, Client, Note, Policy, UserSettings


class ActivityForm(forms.ModelForm):
    policy = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'class': 'form-select'}), required=False)

    class Meta:
        model = Activity
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
        client = kwargs.pop('customer_instance')
        super(ActivityForm, self).__init__(*args, **kwargs)
        policy_choices = client.policies.all()
        self.fields['policy'].queryset = policy_choices

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
                    ["priority", "status"], ["activity_type", "policy"]
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


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)

        address_fields = {
            "name": "Address",
            "fields": [
                ["street_address", "street_address_2"],
                ["city", "state", "zip_code"],
            ]
        }

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.widget_type == "date":
                visible.field.widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
            elif visible.name == "phone" or visible.name == "secondary_phone" or visible.name == "other_phone":
                visible.field.widget.attrs['class'] += ' phone'

            if visible.name == "street_address":
                visible.field.widget.attrs['placeholder'] = 'Street Address'
                visible.field.widget.attrs['autocomplete'] = 'off'
            elif visible.name == "street_address_2":
                visible.field.widget.attrs['placeholder'] = 'Apartment, unit, suite, or floor #'
                visible.field.widget.attrs['autocomplete'] = 'off'
            elif visible.name == "city":
                visible.field.widget.attrs['placeholder'] = 'City'
                visible.field.widget.attrs['autocomplete'] = 'off'
            elif visible.name == "state":
                visible.field.widget.attrs['placeholder'] = 'State'
                visible.field.widget.attrs['autocomplete'] = 'off'
            elif visible.name == "zip_code":
                visible.field.widget.attrs['placeholder'] = 'Zip'
                visible.field.widget.attrs['autocomplete'] = 'off'

        self.fieldsets = [
            {
                "name": "Add Customer",
                "fields": [
                    ["first_name", "last_name"],
                    ["email", address_fields],
                    ["phone", "secondary_phone"],
                    ["other_phone", "date_of_birth"],
                    "notes"
                ],
            },
        ]

    def iter_fieldsets(self):
        for fieldset in self.fieldsets:
            f = {"name": fieldset["name"], "fields": []}
            for field in fieldset["fields"]:
                if type(field) is list:
                    fields = []
                    for subfield in field:
                        if type(subfield) is dict:
                            subfields = {"name": subfield["name"], "fields": []}
                            for s in subfield["fields"]:
                                if type(s) is list:
                                    flds = []
                                    for sf in s:
                                        flds.append(self[sf])
                                    subfields["fields"].append(flds)
                                else:
                                    subfields["fields"].append(self[s])
                            fields.append(subfields)
                        else:
                            fields.append(self[subfield])
                    f["fields"].append(fields)
                else:
                    f["fields"].append(self[field])

            yield f


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = "__all__"
        widgets = {
            "activity": forms.TextInput(attrs={"class": "form-control", "type": "text", "readonly": "readonly"}),
            "created_at": forms.HiddenInput(),
        }


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = "__all__"
        widgets = {
            "client": forms.TextInput(attrs={"class": "form-control readonly", "readonly": "readonly"}),
            "provider": forms.TextInput(attrs={"class": "form-control"}),
            "policy_number": forms.TextInput(attrs={"class": "form-control"}),
            "policy_type": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "premium_amount": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super(PolicyForm, self).__init__(*args, **kwargs)

        self.fieldsets = [
            {
                "name": "Policy Details",
                "fields": [
                    ["client", "provider"],
                    ["policy_number", "policy_type"],
                    ["start_date", "end_date"],
                    ["premium_amount", "status"]
                ],
            },
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


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        exclude = ["user", "created_at", "receive_notifications"]
        fields = ["phone_number", "date_of_birth", "profile_picture", "bio", "theme_preference"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control phone", "autofocus": "autofocus"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "profile_picture": forms.FileInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
            "theme_preference": forms.Select(attrs={"class": "form-select"}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
