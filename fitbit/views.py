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
    user_id = request.GET.get('user_id')
    if not user_id:
        return redirect(FITBIT_PERMISSION_SCREEN)
    fitbit_info = Token.objects.all().filter(fitbit_id=user_id)
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
    response = do_fitbit_auth(
        FITBIT_AUTH_URL.format(code=code, client_id=CLIENT_ID),
    )
    return redirect("{}?user_id={}".format(reverse('index'), response['user_id']))


@login_required
def post_weight_to_slack(request, weight):
    post_message("{} weighs {}".format(request.user.get_username(), weight))
    return HttpResponse("Weight Posted")
