from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


class BusGoSignUpForm(UserCreationForm):
    """Signup form for BusGo passengers."""
    first_name = forms.CharField(max_length=80, required=True, label="Full name")
    email = forms.EmailField(required=True, label="Email address")

    class Meta:
        model = User
        fields = ("first_name", "email", "username", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Please login instead.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.first_name = self.cleaned_data["first_name"].strip()
        if commit:
            user.save()
        return user


def signup_page(request):
    """Create a new passenger account and login automatically."""
    if request.user.is_authenticated:
        return redirect("account_dashboard")

    if request.method == "POST":
        form = BusGoSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to BusGo!")
            return redirect("account_dashboard")
    else:
        form = BusGoSignUpForm()

    return render(request, "signup.html", {"form": form})


def login_page(request):
    """Login existing passenger account."""
    if request.user.is_authenticated:
        return redirect("account_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                next_url = request.GET.get("next")
                return redirect(next_url or "account_dashboard")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_page(request):
    """Logout user and return to login page."""
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("login")


@login_required
def account_dashboard(request):
    """Simple logged-in user dashboard."""
    return render(request, "account_dashboard.html")
