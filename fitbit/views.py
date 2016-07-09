import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from fitbit.fitbit_client import FITBIT_PERMISSION_SCREEN, refresh, FITBIT_AUTH_URL, CLIENT_ID, do_fitbit_auth, \
   get_profile, get_activity_for_day, get_food_for_day
from fitbit.models import Token
from fitbit.slack import post_message
from pytz import timezone


@login_required
def index(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return redirect(FITBIT_PERMISSION_SCREEN)
    fitbit_info = Token.objects.all().filter(fitbit_id=user_id)
    fitbit_auth = refresh(fitbit_info[0])

    tz = timezone('EST')
    today = datetime.datetime.now(tz)

    profile = get_profile(fitbit_auth)
    food = get_food_for_day(fitbit_auth, today)
    activity = get_activity_for_day(fitbit_auth, today)
    pronoun = 'They'
    if profile['gender'] == 'MALE':
        pronoun = 'He'
    elif profile['gender'] == 'FEMALE':
        pronoun = 'She'

    message = "Today {name} weighs {weight} pounds. {pronoun} ate {calories} calories and walked {miles} miles".format(
        name=profile['fullName'],
        weight=profile['weight'],
        pronoun=pronoun,
        calories=food['summary']['calories'],
        miles=next(filter(lambda x: x['activity'] == 'tracker', activity['summary']['distances']))['distance']
    )

    return render(
        request,
        "fitbit/view_message.html",
        context={
            "message": message
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
def post_weight_to_slack(request):
    post_message(request.POST['message'])
    return HttpResponse("Weight Posted")
