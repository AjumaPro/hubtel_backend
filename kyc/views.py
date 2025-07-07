from django.shortcuts import render
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from .models import KYCSubmission, ContactFormSubmission
from django.contrib.auth import get_user_model
import json
import io
import pandas as pd
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view

# Create your views here.

class KYCSubmissionView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Save KYC data with status and notes
        user = request.user if request.user.is_authenticated else None
        data = request.data.get('data') or request.data
        submission_status = request.data.get('status', 'PENDING')
        notes = request.data.get('notes', '')
        
        submission = KYCSubmission.objects.create(
            user=user, 
            data=data, 
            status=submission_status,
            notes=notes
        )
        return Response({
            'id': submission.id, 
            'status': 'saved',
            'submission_status': submission.status
        }, status=status.HTTP_201_CREATED)

class KYCExportExcelView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            submissions = KYCSubmission.objects.all()
            if not submissions.exists():
                return Response({'message': 'No KYC submissions found'}, status=status.HTTP_404_NOT_FOUND)
            
            records = []
            for s in submissions:
                record = s.data.copy()
                record['submission_id'] = s.id
                record['submission_status'] = s.status
                record['notes'] = s.notes or ''
                record['submitted_at'] = s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                record['user'] = str(s.user) if s.user else 'Anonymous'
                records.append(record)
            
            df = pd.DataFrame(records)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='KYC Submissions')
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="kyc_submissions.xlsx"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KYCExportPDFView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            submissions = KYCSubmission.objects.all()
            if not submissions.exists():
                return Response({'message': 'No KYC submissions found'}, status=status.HTTP_404_NOT_FOUND)
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            y = 800
            page = 1
            
            for s in submissions:
                # Add page number
                p.drawString(50, y, f"Page {page}")
                y -= 20
                
                # Add submission header
                p.drawString(50, y, f"Submission ID: {s.id} | User: {s.user or 'Anonymous'} | Status: {s.status} | Date: {s.submitted_at}")
                y -= 20
                
                # Add notes if available
                if s.notes:
                    p.drawString(70, y, f"Notes: {s.notes}")
                    y -= 15
                
                # Add data fields
                for k, v in s.data.items():
                    if y < 100:  # Start new page
                        p.showPage()
                        page += 1
                        y = 800
                        p.drawString(50, y, f"Page {page}")
                        y -= 20
                    
                    p.drawString(70, y, f"{k}: {v}")
                    y -= 15
                
                y -= 20  # Space between submissions
                
                if y < 100:  # Start new page
                    p.showPage()
                    page += 1
                    y = 800
            
            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="kyc_submissions.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def kyc_detail(request, kyc_id):
    """Get detailed KYC submission data"""
    try:
        submission = KYCSubmission.objects.get(id=kyc_id)
        return Response({
            'id': submission.id,
            'user': str(submission.user) if submission.user else None,
            'status': submission.status,
            'notes': submission.notes,
            'submitted_at': submission.submitted_at,
            'data': submission.data,
        })
    except KYCSubmission.DoesNotExist:
        return Response({'error': 'KYC submission not found'}, status=status.HTTP_404_NOT_FOUND)

class ContactFormSubmissionView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle contact form submissions"""
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'message']
            for field in required_fields:
                if not request.data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create contact form submission
            submission = ContactFormSubmission.objects.create(
                name=request.data['name'],
                email=request.data['email'],
                message=request.data['message']
            )
            
            return Response({
                'success': True,
                'message': 'Contact form submitted successfully',
                'data': {
                    'id': submission.id,
                    'submitted_at': submission.submitted_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to submit contact form',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
