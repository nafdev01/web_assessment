from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_client
from django.contrib.auth import logout as logout_client
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import ClientRegistrationForm


# Create your views here.
def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("home")

    if request.method != "POST":
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            client = authenticate(
                request,
                username=username,
                password=password,
            )

            if client is not None:
                login_client(request, client)
                messages.success(request, "You have been logged in.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")

    template_path = "registration/login.html"
    context = {"form": form}
    return render(request, template_path, context)


def register(request):
    if request.method != "POST":
        client_form = ClientRegistrationForm()
    else:
        client_form = ClientRegistrationForm(request.POST)
        if client_form.is_valid():
            # create a new user object without saving it
            new_client = client_form.save(commit=False)
            # set chosen password
            new_client.set_password(client_form.cleaned_data["password1"])
            # save the user object
            client_form.save()

            messages.success(request, "Registration Successful! Log in to continue")
            return redirect("login")

    template_path = "registration/signup.html"
    context = {"form": client_form}
    return render(request, template_path, context)


def log_out(request):
    logout_client(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
