from django.urls import path
from . import views
from .views import RegisterView, VerifyOTPView, SetPasswordView, VerifyPasswordView

app_name = 'payments'

urlpatterns = [
    # API root
    path('', views.api_root, name='api_root'),
    # Payment endpoints
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('initiate-legacy/', views.initiate_payment_legacy, name='initiate_payment_legacy'),
    path('generate-reference/', views.generate_reference, name='generate_reference'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('status/<uuid:transaction_id>/', views.payment_status, name='payment_status'),
    path('callback/', views.payment_callback, name='payment_callback'),
    
    # PHP Laravel-style endpoints
    path('store-callback/', views.store_callback, name='store_callback'),
    path('check-transaction/<str:reference>/', views.check_transaction, name='check_transaction'),
    path('send-sms/', views.send_sms, name='send_sms'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction-detail'),
    path('follow-up/', views.follow_up_payment, name='follow-up-payment'),
    path('export/excel/', views.PaymentExportExcelView.as_view(), name='payment-export-excel'),
    path('export/pdf/', views.PaymentExportPDFView.as_view(), name='payment-export-pdf'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp-auth/', VerifyOTPView.as_view(), name='verify-otp-auth'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('verify-password/', VerifyPasswordView.as_view(), name='verify-password'),
] 