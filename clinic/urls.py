from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Auth
    path('register/', views.register, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    # Patients (Mother Enrolment)
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/add/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:pk>/miss/', views.appointment_miss, name='appointment_miss'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('appointments/<int:pk>/record-attendance/', views.record_attendance, name='record_attendance'),

    # SMS Logs
    path('patients/<int:pk>/send-sms/', views.send_sms_to_patient, name='send_sms_to_patient'),
    path('sms-logs/', views.sms_log_list, name='sms_log_list'),

    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export-csv/', views.export_csv, name='export_csv'),
    path("test-sms/", views.test_bulk_sms, name="test_sms"),

]

# from django.urls import path
# from . import views

# urlpatterns = [
# ]