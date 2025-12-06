from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.authtoken.models import Token

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import GlucoseRecord, FoodIntake
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pandas as pd
from .ml.lstm_model import predict_next_value
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from django.contrib import messages


@csrf_exempt
def receive_iot_data(request):
    if request.method == "POST":
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Token "):
            return JsonResponse({"error": "No token"}, status=401)
        token_value = auth.split()[1]
        try:
            token = Token.objects.get(key=token_value)
        except Token.DoesNotExist:
            return JsonResponse({"error": "Invalid token"}, status=401)
        user = token.user

        data = json.loads(request.body)

        device_id = data.get("device_id")
        glucose = data.get("glucose")
        unit = data.get("unit", "mmol")

        GlucoseRecord.objects.create(
            users=user,
            device_id=device_id,
            glucose=glucose,
            unit=unit
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "POST only"}, status=400)

def dashboard(request):
    user = request.user
    records = GlucoseRecord.objects.filter(users=user).order_by("timestamp")
    meals = FoodIntake.objects.filter(user=user).order_by("-timestamp")
    if not records.exists():
        return render(request, "glucose_app/dashboard.html", {
            "day": [],
            "week": [],
            "month": [],
            "three_month": [],
            "alert": None,
        })
    df = pd.DataFrame(list(records.values()))
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    now = timezone.now()
    day_df = df[df["timestamp"] > now - timedelta(days=1)]
    week_df = df[df["timestamp"] > now - timedelta(days=7)]
    month_df = df[df["timestamp"] > now - timedelta(days=30)]
    three_month_df = df[df["timestamp"] > now - timedelta(days=90)]

    for d in [day_df, week_df, month_df, three_month_df]:
        if not d.empty:
            d["timestamp"] = d["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    alert = alert_check(request.user)

    return render(request, "glucose_app/dashboard.html", {
        "day": day_df.to_dict("records"),
        "week": week_df.to_dict("records"),
        "month": month_df.to_dict("records"),
        "three_month": three_month_df.to_dict("records"),
        "alert": alert,
        "meals": meals,
    })

def predict_glucose(request):
    user = request.user
    records = GlucoseRecord.objects.filter(users=user).order_by("timestamp")
    glucose_values = [r.glucose for r in records][-50:]
    prediction, risk = predict_next_value(glucose_values)
    return JsonResponse({
        "prediction": float(prediction),
        "risk": risk
    })

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/register.html", {"error": "Username exists"})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("/profile/")
    return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("/profile/")
        return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/login.html", {"error": "Invalid credentials"})

    return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/login.html")

def logout_view(request):
    logout(request)
    return redirect("/login/")

def alert_check(user):
    records = GlucoseRecord.objects.filter(users=user).order_by("timestamp")
    if len(records) < 15:
        return None
    values = [r.glucose for r in records][-20:]
    pred, risk = predict_next_value(values)
    if risk == "Normal":
        return None
    return {
        "prediction": pred,
        "risk": risk
    }

def home_view(request):
    return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/home.html")

def profile_view(request):
    return render(request, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/templates/glucose_app/profile.html")

def add_food(request):
    if request.method == "POST":
        name = request.POST.get("name")
        calories = request.POST.get("calories")
        description = request.POST.get("description", "")

        if not name:
            messages.error(request, "Please entry a meal name")
            return redirect("/dashboard/")
        try:
            calories = float(calories) if calories else None
        except ValueError:
            messages.error(request, "Invalid calories value")
            return redirect("/dashboard/")

        FoodIntake.objects.create(
            user=request.user,
            name=name,
            calories=calories,
            description=description,
        )

        messages.success(request, "Meal added!")
        return redirect("/dashboard/")
    return redirect("/dashboard/")

def add_manual_glucose(request):
    if request.method == "POST":
        glucose = request.POST.get("glucose")
        unit = request.POST.get("unit", "mmol")
        if not glucose:
            messages.error(request, "Please enter a glucose value")
            return redirect("/dashboard/")

        try:
            glucose = float(glucose)
        except ValueError:
            messages.error(request, "Invalid glucose value")
            return redirect("/dashboard/")

        GlucoseRecord.objects.create(
            users=request.user,
            device_id="manual",
            glucose=glucose,
            unit=unit
        )

        messages.success(request, "Glucose measurement added!")

        return redirect("/dashboard/")
    return redirect("/dashboard/")

def delete_food(request, meal_id):
    meal = get_object_or_404(FoodIntake, id=meal_id, user=request.user)
    meal.delete()
    messages.success(request, "Meal deleted!")
    return redirect("/dashboard/")

def delete_glucose(request, record_id):
    record = get_object_or_404(GlucoseRecord, id=record_id, users=request.user)
    record.delete()
    messages.success(request, "Glucose record deleted!")
    return redirect("/dashboard/")
