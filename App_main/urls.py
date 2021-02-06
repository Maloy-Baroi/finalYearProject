from django.urls import path
from App_main import views

app_name = "App_main"

urlpatterns = [
    path('login', views.index, name="login"),
    # path('signup', views.signup, name="signup"),
    path('', views.home, name="home"),
    path('logout', views.loggedout, name='logout'),
    path('register_report', views.report_register, name='register_report'),
    path('view_suspected', views.view_records, name='view_suspected'),
    path('detect_suspected', views.detectWithWebcam, name='detectSuspected'),
    path('profile', views.police_profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
    path('view_supected_info', views.view_suspected_info, name="view_suspected_info")
]
