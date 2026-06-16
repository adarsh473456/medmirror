from django.urls import path
from . import views

app_name = 'medmirror'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('patient-input/', views.patient_input_view, name='patient_input'),
    path('mirror-world/', views.mirror_world_view, name='mirror_world'),
    path('simulation/', views.simulation_view, name='simulation'),
    path('simulation-status/', views.simulation_status_api, name='simulation_status_api'),
    path('report/', views.report_view, name='report'),
    path('report/download/', views.download_pdf_view, name='download_pdf'),
    path('reset/', views.reset_view, name='reset'),
]
