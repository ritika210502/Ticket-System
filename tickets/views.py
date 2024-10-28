from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Ticket, Assignment
from .forms import UserRegistrationForm,TicketCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        email = request.POST.get('username')  # Capture the email field from form
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)  # Authenticate using email
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            form.add_error(None, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

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
            # Get the assigned users
            assigned_users = form.cleaned_data['assigned_users']
            # Assign the ticket to the selected users
            for user in assigned_users:
                Assignment.objects.create(ticket=ticket, assigned_user=user)
                # Send a notification email to the user
                send_assignment_notification(user, ticket)
            return redirect('ticket_list')
    else:
        form = TicketCreationForm()
    return render(request, 'create_ticket.html', {'form': form})

def send_assignment_notification(user, ticket):
    # Send email notification to the assigned user
    subject = f"You have been assigned to a ticket: {ticket.title}"
    message = f"Hello {user.username},\n\nYou have been assigned to the ticket: {ticket.title}.\n\nDetails:\nTitle: {ticket.title}\nPriority: {ticket.priority}\nStatus: {ticket.status}\n\nThank you."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@login_required
def ticket_list_view(request):
    # Get tickets created by the user or assigned to the user
    created_tickets = Ticket.objects.filter(created_by=request.user)
    assigned_tickets = Ticket.objects.filter(assignments__assigned_user=request.user).distinct()
    return render(request, 'ticket_list.html', {'created_tickets': created_tickets, 'assigned_tickets': assigned_tickets})
