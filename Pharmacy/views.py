import random
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Pharmacy
from .forms import PharmacyForm, UserRegistrationForm, SellForm


# ==========================================
# Authentication Views
# ==========================================

def user_register(request):
    """Handle user registration using a custom form.

    - GET: display the registration form
    - POST: validate form data, create new user, and redirect to login
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Create a new user automatically hashing the password
            User.objects.create_user(username=username, password=password)

            messages.success(
                request,
                f"Account created successfully for {username}! Please log in."
            )
            return redirect('pharmacy:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'pharmacy/register.html', {'form': form})


def user_login(request):
    """Handle user login using Django's built-in authentication system.

    - GET: display the login form
    - POST: authenticate credentials and log the user in
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('pharmacy:medicine_list')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'pharmacy/login.html')


def user_logout(request):
    """Log out the current user and redirect to login page."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('pharmacy:login')


# ==========================================
# Inventory & Core Business Logic Views
# ==========================================

@login_required(login_url='pharmacy:login')
def list_medicines(request):
    """Retrieve all medicines and calculate global inventory summary metrics."""
    medicines = Pharmacy.objects.all()
    today = timezone.now().date()

    # Calculate total value of available sellable stock in INR
    total_value = sum(m.unit_price * m.stock_available for m in medicines)

    # Low stock tracking items threshold (<= 10 units)
    low_stock_count = Pharmacy.objects.filter(stock_available__lte=10).count()

    # Filter count for items exceeding their designated expiration milestone date
    expired_count = Pharmacy.objects.filter(expiry_date__lt=today).count()

    context = {
        'medicines': medicines,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
    }
    return render(request, 'pharmacy/list_medicine.html', context)


@login_required(login_url='pharmacy:login')
def admin_dashboard(request):
    """Show user accounts and operational inventory details to staff only."""
    if not request.user.is_staff:
        raise PermissionDenied

    search_query = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('-date_joined')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    medicines = Pharmacy.objects.all()
    context = {
        'users': users,
        'search_query': search_query,
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'staff_user_count': User.objects.filter(is_staff=True).count(),
        'superuser_count': User.objects.filter(is_superuser=True).count(),
        'medicine_count': medicines.count(),
        'inventory_value': sum(
            medicine.unit_price * medicine.stock_available for medicine in medicines
        ),
        'medicines': medicines,
    }
    return render(request, 'pharmacy/admin_dashboard.html', context)


@login_required(login_url='pharmacy:login')
@require_POST
def delete_user(request, pk):
    """Delete a user account while protecting the signed-in and last superuser."""
    if not request.user.is_staff:
        raise PermissionDenied

    account = get_object_or_404(User, pk=pk)
    if account.pk == request.user.pk:
        messages.error(request, "You cannot delete your own account.")
    elif account.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
        messages.error(request, "The last superuser account cannot be deleted.")
    else:
        username = account.username
        account.delete()
        messages.success(request, f"User '{username}' was deleted.")

    return redirect('pharmacy:admin_dashboard')


@login_required(login_url='pharmacy:login')
def add_medicine(request):
    """Handle adding a new Medicine item profile record entry."""
    if request.method == 'POST':
        form = PharmacyForm(request.POST)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, f"✅ Medicine '{medicine.medicine_name}' added successfully!")
            return redirect('pharmacy:medicine_list')
    else:
        form = PharmacyForm()

    return render(request, 'pharmacy/add_medicine.html', {'form': form})


@login_required(login_url='pharmacy:login')
def edit_medicine(request, pk):
    """Load an existing Pharmacy item record to perform modify updates."""
    instance = get_object_or_404(Pharmacy, pk=pk)

    if request.method == 'POST':
        form = PharmacyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Medicine '{instance.medicine_name}' updated successfully!")
            return redirect('pharmacy:medicine_list')
    else:
        form = PharmacyForm(instance=instance)

    return render(request, 'pharmacy/edit_medicine.html', {'form': form, 'medicine': instance})


@login_required(login_url='pharmacy:login')
def medicine_sell(request, pk):
    """Process item orders from billing selection prompts and generate receipts."""
    medicine = get_object_or_404(Pharmacy, pk=pk)

    if request.method == 'POST':
        form = SellForm(request.POST)
        if form.is_valid():
            # Extract values dynamically from the posted form dataset
            selected_medicine = form.cleaned_data['medicine']
            quantity = form.cleaned_data['quantity']

            # Use Decimal conversion to operate accurately alongside DecimalFields
            quantity_dec = Decimal(quantity)

            # Inventory validation guardrail check
            if quantity_dec > selected_medicine.stock_available:
                messages.error(
                    request,
                    f"Insufficient stock! Only {selected_medicine.stock_available} units left for this selection."
                )
                return redirect('pharmacy:medicine_sell', pk=pk)

            # Compute transactional values
            total_amount = selected_medicine.unit_price * quantity_dec

            # Complete the checkout subtraction task operations
            selected_medicine.stock_available -= quantity_dec
            selected_medicine.save()

            messages.success(request, f"Sale processed successfully for {selected_medicine.medicine_name}!")

            # ─── REDIRECTED TO MEDICINE LIST PAGE ───
            return redirect('pharmacy:medicine_list')
    else:
        # Prepopulate layout choices safely matching targeted items initialization views
        form = SellForm(initial={'medicine': medicine.pk, 'quantity': 1})

    medicines = Pharmacy.objects.all()
    return render(request, 'pharmacy/sell_medicine.html', {
        'form': form,
        'medicine': medicine,
        'medicines': medicines,
        'selected': medicine
    })


@login_required(login_url='pharmacy:login')
def delete_medicine(request, pk):
    """Confirm verification and drop matching profile model table items completely."""
    instance = get_object_or_404(Pharmacy, pk=pk)

    if request.method == 'POST':
        medicine_name = instance.medicine_name
        instance.delete()
        messages.success(request, f"✅ Medicine '{medicine_name}' deleted successfully!")
        return redirect('pharmacy:medicine_list')

    return render(request, 'pharmacy/delete_medicine_confirm.html', {'medicine': instance})