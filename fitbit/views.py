from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
from django.template import Context


@login_required
def index(request):
    return render(request, "fitbit/view_message.html", context={"username": request.user.get_username()})



