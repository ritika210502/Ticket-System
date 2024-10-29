from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Ticket, Assignment,Activity,Notification
from .forms import UserRegistrationForm,TicketCreationForm,TicketStatusUpdateForm,CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from itertools import chain
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def home_view(request):
    return redirect('ticket_list')  

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form.add_error(None, "Invalid detail provide")
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        email = request.POST.get('username')  # Capture the email field from form
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)  # Authenticate using email
        if user is not None:
            login(request, user)
            return redirect('ticket_list')
        else:
            form.add_error(None, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def create_ticket_view(request):
    if request.method == 'POST':
        form = TicketCreationForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            # Log ticket creation activity
            Activity.objects.create(
                ticket=ticket,
                user=request.user,
                action="Ticket created"
            )
            send_notification('create', ticket, request.user)  # Send notification for ticket creation

            # Assign users and log assignment activity
            assigned_users = form.cleaned_data['assigned_users']
            for user in assigned_users:
                Assignment.objects.create(ticket=ticket, assigned_user=user)
                Activity.objects.create(
                    ticket=ticket,
                    user=user,
                    action="Assigned to ticket"
                )
                send_notification('assign', ticket, user, {'assigner': request.user})  # Send assignment notification

            return redirect('ticket_list')
    else:
        form = TicketCreationForm()
    return render(request, 'ticket/create_ticket.html', {'form': form})

@login_required
def update_ticket_status_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check if the user is authorized to update the ticket
    if request.user != ticket.created_by and not ticket.assignments.filter(assigned_user=request.user).exists():
        messages.error(request, "You are not authorized to update this ticket.")
        return redirect('ticket_list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status != ticket.status:
            ticket.status = new_status
            ticket.save()
            # Log the status update as an activity
            Activity.objects.create(
                ticket=ticket,
                user=request.user,
                action=f"Status updated to {new_status}"
            )
            send_notification('update_status', ticket, request.user, {'new_status': new_status})  # Send status update notification
        return redirect('ticket/ticket_activity', ticket_id=ticket.id)

    return render(request, 'ticket/update_ticket_status.html', {'ticket': ticket})

@login_required
def add_comment_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check if the user is authorized to comment on the ticket
    if request.user != ticket.created_by and not ticket.assignments.filter(assigned_user=request.user).exists():
        messages.error(request, "You are not authorized to comment on this ticket.")
        return redirect('ticket_list')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            # Log the comment as an activity
            Activity.objects.create(
                ticket=ticket,
                user=request.user,
                action=f"Comment: {comment}"
            )
            send_notification('comment', ticket, request.user, {'comment': comment})  # Send comment notification
            return redirect('ticket/ticket_activity', ticket_id=ticket.id)
    else:
        form = CommentForm()
    return render(request, 'ticket/add_comment.html', {'form': form, 'ticket': ticket})


def send_notification(action_type, ticket, user, additional_info=None):
    try:
        # Prepare the email subject and message based on the action type
        if action_type == 'create':
            subject = f"A new ticket has been created: {ticket.title}"
            message = f"Hello,\n\n{user.username} has created a new ticket:\n\n" \
                      f"Title: {ticket.title}\nPriority: {ticket.priority}\nStatus: {ticket.status}\n\nThank you."
            assigned_users = ticket.assignments.values_list('assigned_user__email', flat=True)

        elif action_type == 'assign':
            subject = f"You have been assigned to a ticket: {ticket.title}"
            message = f"Hello {user.username},\n\n{additional_info['assigner'].username} has assigned you to the ticket: {ticket.title}.\n\n" \
                      f"Details:\nTitle: {ticket.title}\nPriority: {ticket.priority}\nStatus: {ticket.status}\n\nThank you."

        elif action_type == 'update_status':
            subject = f"Ticket status updated: {ticket.title}"
            message = f"Hello,\n\n{user.username} has updated the status of the ticket '{ticket.title}' to '{additional_info['new_status']}'.\n\nThank you."
            assigned_users = ticket.assignments.values_list('assigned_user__email', flat=True)

        elif action_type == 'comment':
            subject = f"New comment on ticket: {ticket.title}"
            message = f"Hello,\n\n{user.username} has added a new comment to the ticket '{ticket.title}':\n\n\"{additional_info['comment']}\"\n\nThank you."
            assigned_users = ticket.assignments.values_list('assigned_user__email', flat=True)

        else:
            return  # Unknown action type

        # Create a notification record in the database
        Notification.objects.create(
            user=user,
            ticket=ticket,
            message=message,
        )

        # Send the email notification
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            list(assigned_users) if 'assigned_users' in locals() else [user.email],
            fail_silently=False,
        )

    except Exception as e:
        print(f"Error in send_notification: {e}")  # Log error for debugging


@login_required
def ticket_list_view(request):
    # Get tickets created by the user
    created_tickets = Ticket.objects.filter(created_by=request.user)
    # Get tickets assigned to the user
    assigned_tickets = Ticket.objects.filter(assignments__assigned_user=request.user).distinct()

    # Combine the two querysets into a single list
    tickets = list(chain(created_tickets, assigned_tickets))

    # Collect ticket details along with their most recent activity
    tickets_with_recent_activity = []
    for ticket in tickets:
        # Fetch the latest activity for each ticket
        recent_activity = ticket.activities.order_by('-timestamp').first()
        # Append ticket info and recent activity to the list
        tickets_with_recent_activity.append({
            'ticket': ticket,
            'recent_activity': recent_activity
        })

    return render(request, 'ticket/ticket_list.html', {
        'tickets_with_recent_activity': tickets_with_recent_activity,
    })


@login_required
def ticket_activity_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check if the user is authorized to view the ticket
    if request.user != ticket.created_by and not ticket.assignments.filter(assigned_user=request.user).exists():
        messages.error(request, "You are not authorized to view this ticket activity.")
        return redirect('ticket_list')  # Redirect back to the list view with an error

    activities = ticket.activities.filter(action__icontains="Status updated").order_by('-timestamp')
    return render(request, 'ticket/ticket_activity.html', {'ticket': ticket, 'activities': activities})

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_as_read_view(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')


@staff_member_required
@login_required
def admin_ticket_list_view(request):
    # Get all tickets in the system
    tickets = Ticket.objects.all()
    tickets_with_recent_activity = []
    
    for ticket in tickets:
        recent_activity = ticket.activities.order_by('-timestamp').first()
        tickets_with_recent_activity.append({
            'ticket': ticket,
            'recent_activity': recent_activity
        })

    return render(request, 'admin/ticket_list.html', {
        'tickets_with_recent_activity': tickets_with_recent_activity,
    })

@staff_member_required
@login_required
def admin_assign_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        assigned_users = request.POST.getlist('assigned_users')  # Assuming a multiple select input
        for user_id in assigned_users:
            user = User.objects.get(id=user_id)
            Assignment.objects.create(ticket=ticket, assigned_user=user)
            # Log assignment activity
            Activity.objects.create(
                ticket=ticket,
                user=request.user,
                action=f"Assigned to ticket {ticket.title}"
            )
        messages.success(request, "Users successfully assigned to the ticket.")
        return redirect('admin_ticket_list')  # Redirect to the ticket list

    # Fetch all users for the assignment form
    users = User.objects.all()
    return render(request, 'admin/assign_ticket.html', {'ticket': ticket, 'users': users})

@staff_member_required
@login_required
def admin_update_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = TicketStatusUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            # Log the update as an activity
            Activity.objects.create(
                ticket=ticket,
                user=request.user,
                action="Ticket updated"
            )
            messages.success(request, "Ticket status updated.")
            return redirect('admin_ticket_list')
    else:
        form = TicketStatusUpdateForm(instance=ticket)

    return render(request, 'admin/update_ticket.html', {'form': form, 'ticket': ticket})

@staff_member_required
@login_required
def admin_ticket_activity_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    activities = ticket.activities.order_by('-timestamp')  # Fetch all activities for the ticket
    return render(request, 'admin/ticket_activity.html', {'ticket': ticket, 'activities': activities})
