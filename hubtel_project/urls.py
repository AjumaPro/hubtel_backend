"""
URL configuration for hubtel_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.utils.html import escape
from django.conf import settings
from django.conf.urls.static import static
from payments.models import PaymentTransaction
import datetime
import json
import requests

def home(request):
    # Branding/logo (inline SVG)
    logo_svg = '''<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="24" fill="#1a237e"/><text x="50%" y="55%" text-anchor="middle" fill="#fff" font-size="22" font-family="Segoe UI,Arial,sans-serif" dy=".3em">GC</text></svg>'''

    # Recent transactions (last 5)
    txs = PaymentTransaction.objects.order_by('-created_at')[:5]
    tx_rows = "".join([
        f"<tr><td>{escape(tx.reference)}</td><td>{escape(str(tx.amount))}</td><td>{escape(tx.currency)}</td><td>{escape(tx.status)}</td><td>{escape(tx.customer_name)}</td><td>{tx.created_at.strftime('%Y-%m-%d %H:%M')}</td></tr>"
        for tx in txs
    ])
    if not tx_rows:
        tx_rows = "<tr><td colspan='6' style='text-align:center;color:#888;'>No transactions yet</td></tr>"

    # Live DB status
    try:
        db_status = '<span style="color:#388e3c;">Online</span>'
    except Exception:
        db_status = '<span style="color:#d32f2f;">Offline</span>'

    # Live Hubtel API status (simple GET to hubtel.com)
    try:
        r = requests.get('https://hubtel.com', timeout=2)
        if r.status_code == 200:
            hubtel_status = '<span style="color:#388e3c;">Online</span>'
        else:
            hubtel_status = '<span style="color:#fbc02d;">Unstable</span>'
    except Exception:
        hubtel_status = '<span style="color:#d32f2f;">Offline</span>'

    # Team/contact info
    team_html = """
        <div class='team'>
            <h2>Contact & Team</h2>
            <ul>
                <li><b>Support:</b> <a href='mailto:support@glicocapital.com'>support@glicocapital.com</a></li>
                <li><b>Phone:</b> +233 302 218 500</li>
                <li><b>Address:</b> GLICO House, Accra, Ghana</li>
            </ul>
        </div>
    """

    # API Explorer (JS forms for endpoints)
    api_explorer = '''
    <div class="api-explorer">
      <h2>API Explorer</h2>
      <form id="initiateForm" onsubmit="return apiCall('initiate')">
        <b>Initiate Payment</b><br>
        <input name="amount" placeholder="Amount" required type="number" step="0.01"> 
        <input name="description" placeholder="Description" required>
        <input name="reference" placeholder="Reference" required>
        <input name="type" value="initial" style="width:80px;" required>
        <button type="submit">Send</button>
      </form>
      <form id="checkForm" onsubmit="return apiCall('check')">
        <b>Check Transaction</b><br>
        <input name="reference" placeholder="Reference" required>
        <button type="submit">Check</button>
      </form>
      <form id="smsForm" onsubmit="return apiCall('sms')">
        <b>Send SMS</b><br>
        <input name="phone_number" placeholder="Phone Number" required>
        <input name="message" placeholder="Message" required>
        <button type="submit">Send</button>
      </form>
      <pre id="apiResult" style="background:#eceff1;padding:1em;border-radius:6px;margin-top:1em;overflow:auto;"></pre>
    </div>
    <script>
    function apiCall(type) {
      let url, data = {}, method = 'POST';
      if(type==='initiate') {
        url = '/api/payments/initiate-legacy/';
        let f = document.getElementById('initiateForm');
        data = {amount: f.amount.value, description: f.description.value, reference: f.reference.value, type: f.type.value};
      } else if(type==='check') {
        url = '/api/payments/check-transaction/' + document.getElementById('checkForm').reference.value + '/';
        method = 'GET';
      } else if(type==='sms') {
        url = '/api/payments/send-sms/';
        let f = document.getElementById('smsForm');
        data = {phone_number: f.phone_number.value, message: f.message.value};
      }
      document.getElementById('apiResult').textContent = 'Loading...';
      fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: method==='POST' ? JSON.stringify(data) : undefined
      }).then(r=>r.json()).then(j=>{
        document.getElementById('apiResult').textContent = JSON.stringify(j, null, 2);
      }).catch(e=>{
        document.getElementById('apiResult').textContent = 'Error: ' + e;
      });
      return false;
    }
    </script>
    '''

    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Hubtel Payment API Backend</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f7f9fa; margin: 0; padding: 0; }}
            .container {{ max-width: 900px; margin: 5vh auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 16px #0001; padding: 2.5rem 2rem; }}
            .branding {{ display: flex; align-items: center; gap: 1.2em; margin-bottom: 1.5em; }}
            .branding h1 {{ color: #1a237e; margin: 0; font-size: 2.2em; }}
            .status-table td {{ padding: 0.3em 1.2em 0.3em 0; }}
            .links {{ margin: 2em 0; }}
            .links a {{ display: inline-block; margin: 0.5em 1em 0.5em 0; color: #1976d2; text-decoration: none; font-weight: 500; }}
            .links a:hover {{ text-decoration: underline; }}
            .api-section {{ background: #f1f8e9; border-left: 4px solid #43a047; padding: 1em 1.5em; margin: 2em 0 1em 0; border-radius: 8px; }}
            code {{ background: #eceff1; border-radius: 4px; padding: 2px 6px; font-size: 1em; }}
            .footer {{ margin-top: 2em; color: #888; font-size: 0.95em; text-align: center; }}
            .recent-tx {{ margin: 2em 0; }}
            .recent-tx table {{ width: 100%; border-collapse: collapse; }}
            .recent-tx th, .recent-tx td {{ border-bottom: 1px solid #e0e0e0; padding: 0.5em; text-align: left; }}
            .recent-tx th {{ background: #f5f5f5; }}
            .api-explorer form {{ margin-bottom: 1.2em; }}
            .api-explorer input, .api-explorer button {{ margin: 0.2em 0.3em 0.2em 0; padding: 0.3em 0.7em; border-radius: 4px; border: 1px solid #bdbdbd; }}
            .api-explorer button {{ background: #1976d2; color: #fff; border: none; cursor: pointer; }}
            .api-explorer button:hover {{ background: #1565c0; }}
            .team ul {{ list-style: none; padding: 0; }}
            .team li {{ margin-bottom: 0.5em; }}
        </style>
    </head>
    <body>
        <div class='container'>
            <div class='branding'>
                {logo_svg}
                <h1>Hubtel Payment API Backend</h1>
            </div>
            <table class='status-table'>
                <tr><td><b>Database:</b></td><td>{db_status}</td><td><b>Hubtel API:</b></td><td>{hubtel_status}</td></tr>
            </table>
            <div class='links'>
                <a href='/admin/'>Admin Panel</a>
                <a href='/api/payments/'>API Root</a>
                <a href='https://hubtel.com/' target='_blank'>Hubtel</a>
                <a href='https://github.com/AjumaPro/Glico_Capital_App' target='_blank'>Project Docs</a>
            </div>
            <div class='api-section'>
                <h2>API Endpoints</h2>
                <ul>
                    <li><b>Initiate Payment:</b> <code>POST /api/payments/initiate-legacy/</code></li>
                    <li><b>Store Callback:</b> <code>POST /api/payments/store-callback/</code></li>
                    <li><b>Check Transaction:</b> <code>GET /api/payments/check-transaction/&lt;reference&gt;/</code></li>
                    <li><b>Send SMS:</b> <code>POST /api/payments/send-sms/</code></li>
                    <li><b>Admin:</b> <code>/admin/</code></li>
                </ul>
            </div>
            <div class='recent-tx'>
                <h2>Recent Transactions</h2>
                <table>
                    <tr><th>Reference</th><th>Amount</th><th>Currency</th><th>Status</th><th>Customer</th><th>Created</th></tr>
                    {tx_rows}
                </table>
            </div>
            {api_explorer}
            {team_html}
            <div class='footer'>
                &copy; 2024 Glico Capital &mdash; Powered by Django & Hubtel API
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/payments/', include('payments.urls')),
    path('api/kyc/', include('kyc.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
