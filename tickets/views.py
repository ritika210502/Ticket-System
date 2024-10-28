from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Ticket, Assignment
from .forms import UserRegistrationForm,TicketCreationForm
from django.contrib.auth.decorators import login_required


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
            
            #assign the ticket to the creator by default
            Assignment.objects.create(ticket=ticket, assigned_user=request.user)
            return redirect('ticket_list')
    else:
        form = TicketCreationForm()
    return render(request, 'create_ticket.html', {'form': form})

@login_required
def ticket_list_view(request):
    # Get tickets created by the user or assigned to the user
    created_tickets = Ticket.objects.filter(created_by=request.user)
    assigned_tickets = Ticket.objects.filter(assignments__assigned_user=request.user).distinct()
    return render(request, 'ticket_list.html', {'created_tickets': created_tickets, 'assigned_tickets': assigned_tickets})
