import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from fitbit.fitbit_client import FITBIT_PERMISSION_SCREEN, refresh, FITBIT_AUTH_URL, CLIENT_ID, do_fitbit_auth, \
   get_profile, get_activity_for_day, get_food_for_day, get_weight_for_day, get_weight_goal
from fitbit.models import Token
from fitbit.slack import post_message
from pytz import timezone


def get_message(user_id):
    fitbit_info = Token.objects.all().filter(fitbit_id=user_id)
    fitbit_auth = refresh(fitbit_info[0])

    tz = timezone('EST')
    today = datetime.datetime.now(tz)

    try:
        profile = get_profile(fitbit_auth)['user']
        weight = get_weight_for_day(fitbit_auth, today)['weight']
        pronoun = 'They'
        if profile['gender'] == 'MALE':
            pronoun = 'He'
        elif profile['gender'] == 'FEMALE':
            pronoun = 'She'
        did_not_weigh_self = "" if len(weight) else " {} did not step on the scale today".format(pronoun)
        profile_url = "https://www.fitbit.com/user/{}".format(profile['encodedId'])
        weight = "Today {name} weighs {weight} pounds. {shame}".format(
            name=profile['fullName'],
            weight=profile['weight'],
            shame=did_not_weigh_self
        )

        profile_message = "Full Report: {profile_url}".format(profile_url=profile_url)
    except KeyError:
        return "User did not grant sufficient permission. I need at least weight and profile"

    try:
        weight_goal = get_weight_goal(fitbit_auth)['goal']
        current_goal = weight_goal['startWeight'] - weight_goal['weight']
        weight_goal_message = (
            "{pronoun} currently has a goal to lose {to_lose:.2f} pounds. "
            "{pronoun} is {percent:.2%} percent of the way there".format(
                pronoun=pronoun,
                to_lose=current_goal,
                percent=((weight_goal['startWeight'] - profile['weight']) / current_goal)
            )
        )
    except KeyError:
        weight_goal_message = ""

    try:
        activity = get_activity_for_day(fitbit_auth, today)
        distance_traveled = next(filter(lambda x: x['activity'] == 'tracker', activity['summary']['distances']))['distance']
        distance = "{pronoun} walked {miles} miles.".format(pronoun=pronoun, miles=distance_traveled)
        calories_burned = "{} burned {} calories.".format(pronoun, activity['summary']['caloriesOut'])
    except KeyError:
        distance = calories_burned = ""

    try:
        food = get_food_for_day(fitbit_auth, today)
        calories_consumed = "{pronoun} ate {calories} calories.".format(
            pronoun=pronoun,
            calories=food['summary']['calories']
        )
    except KeyError:
        calories_consumed = ""

    return "\n".join([x for x in [weight, weight_goal_message, calories_consumed, calories_burned, distance, profile_message] if x])


@login_required
def index(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return redirect(FITBIT_PERMISSION_SCREEN)

    return render(
        request,
        "fitbit/view_message.html",
        context={
            "message": get_message(user_id)
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
