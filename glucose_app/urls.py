from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view),
    path("api/iot-data/", views.receive_iot_data),
    path("dashboard/", views.dashboard),
    path("profile/", views.profile_view),
    path("predict/", views.predict_glucose),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("register/", views.register_view),
    path("add-food/", views.add_food, name="add_food"),
    path("add-manual/", views.add_manual_glucose, name="add_manual"),
    path("delete_food/<int:meal_id>/", views.delete_food, name="delete_food"),
    path("delete_glucose/<int:record_id>/", views.delete_glucose, name="delete_glucose")
]
