from django.contrib import admin
from .models import Ticket, Assignment, Activity

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1  # Number of empty forms to display

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1  # Allow adding multiple users

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_by')
    search_fields = ('title', 'description')
    inlines = [AssignmentInline, ActivityInline]  # Show assignments and activities inline

    def get_queryset(self, request):
        # Admins can view all tickets
        return super().get_queryset(request)

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'assigned_user')

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'action', 'timestamp')
    list_filter = ('ticket', 'user')
    search_fields = ('action',)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Activity, ActivityAdmin)
