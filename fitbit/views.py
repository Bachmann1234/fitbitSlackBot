from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from fitbit.fitbit_client import FITBIT_PERMISSION_SCREEN, refresh, FITBIT_AUTH_URL, CLIENT_ID, do_fitbit_auth, \
    get_weight
from fitbit.models import Token
from fitbit.slack import post_message


@login_required
def index(request):
    fitbit_info = Token.objects.all().filter(user=request.user.id)
    if not fitbit_info:
        return redirect(FITBIT_PERMISSION_SCREEN)
    fitbit_auth = refresh(fitbit_info[0])
    weight = get_weight(fitbit_auth)

    return render(
        request,
        "fitbit/view_message.html",
        context={
            "username": request.user.get_username(),
            "weight": weight
        }
    )


@login_required
def fitbit_redirect(request):
    code = request.GET['code']
    do_fitbit_auth(
        FITBIT_AUTH_URL.format(code=code, client_id=CLIENT_ID),
        Token.objects.get_or_create(user=request.user, fitbit_id='', refresh_token='')[0]
    )
    return redirect(reverse('index'))


@login_required
def post_weight_to_slack(request, weight):
    post_message("{} weighs {}".format(request.user.get_username(), weight))
    return HttpResponse("Weight Posted")
