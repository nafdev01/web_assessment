import logging

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_client
from django.contrib.auth import logout as logout_client
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import ClientRegistrationForm, ClientUpdateForm, ContactForm

logger = logging.getLogger(__name__)


# Create your views here.
def login(request):
    if request.user.is_authenticated:
        logger.info(
            f"Already authenticated user {request.user.username} attempted to access login page"
        )
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
                logger.info(
                    f"User {username} logged in successfully from IP {request.META.get('REMOTE_ADDR')}"
                )
                messages.success(request, "You have been logged in.")
                return redirect("home")
            else:
                logger.warning(
                    f"Failed login attempt for username: {username} from IP {request.META.get('REMOTE_ADDR')}"
                )
                messages.error(request, "Invalid username or password.")
        else:
            logger.warning(
                f"Invalid login form submission from IP {request.META.get('REMOTE_ADDR')}"
            )

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

            username = new_client.username
            logger.info(
                f"New user registered: {username} from IP {request.META.get('REMOTE_ADDR')}"
            )
            messages.success(request, "Registration Successful! Log in to continue")
            return redirect("login")
        else:
            logger.warning(
                f"Registration form validation failed from IP {request.META.get('REMOTE_ADDR')}: {client_form.errors}"
            )

    template_path = "registration/signup.html"
    context = {"form": client_form}
    return render(request, template_path, context)


def log_out(request):
    username = request.user.username if request.user.is_authenticated else "Anonymous"
    logout_client(request)
    logger.info(f"User {username} logged out from IP {request.META.get('REMOTE_ADDR')}")
    messages.success(request, "You have been logged out.")
    return redirect("home")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Contact form submitted by {form.cleaned_data.get('email')}")
            messages.success(
                request,
                "Your contact request has been processed. We will reply as soon as possible",
            )
            return redirect("home")
        else:
            logger.warning(f"Contact form validation failed: {form.errors}")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ClientUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ClientUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})
