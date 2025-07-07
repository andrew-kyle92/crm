from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Client, Activity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None,
         {
             'fields': (
                 'email', 'first_name', 'last_name')}),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    model = Activity
    list_display = ('client', 'subject', 'activity_type', 'due_date', 'status')
    list_filter = ('client', 'subject', 'activity_type', 'due_date', 'status')
    fieldsets = (
        ('Task Details', {
            'fields': (
                ('subject', 'assigned_to'),
                ('client', 'due_date'),
                'description',
            )
        }),
        ('Additional Details', {
            'fields': (
                ('priority', 'status'),
                ('activity_type', 'policy')
            )
        })
    )
