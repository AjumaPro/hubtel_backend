from django.urls import path
from .views import KYCSubmissionView, KYCExportExcelView, KYCExportPDFView, kyc_detail, ContactFormSubmissionView

urlpatterns = [
    path('submit/', KYCSubmissionView.as_view(), name='kyc-submit'),
    path('export/excel/', KYCExportExcelView.as_view(), name='kyc-export-excel'),
    path('export/pdf/', KYCExportPDFView.as_view(), name='kyc-export-pdf'),
    path('<int:kyc_id>/', kyc_detail, name='kyc-detail'),
    path('contact/submit/', ContactFormSubmissionView.as_view(), name='contact-submit'),
] 