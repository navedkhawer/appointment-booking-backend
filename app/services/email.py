import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
ADMIN_EMAIL = "naveedkhawer688@gmail.com"

# --- HELPER: SEND EMAIL ---
def _send_email(to_email: str, subject: str, html_content: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"HelseMed Care Norway <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# --- SHARED FOOTER ---
EMAIL_FOOTER = """
    <div style="background-color: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 12px; line-height: 1.6;">
        <p style="margin: 0 0 10px 0; font-weight: bold; color: #475569; font-size: 14px;">HelseMed Care Norway</p>
        <p style="margin: 0; line-height: 1.5;">
            <strong>Email Us:</strong> <a href="mailto:helsemed@icloud.com" style="color: #817bf4; text-decoration: none;">helsemed@icloud.com</a><br>
            <strong>Call Us Directly:</strong> +47-94080888
        </p>
        <p style="margin: 12px 0 0 0;">
            <strong>Visit Office:</strong><br>
            Oberst Rodes vei 57A, 1152 Oslo
        </p>
        <p style="margin-top: 20px; font-size: 11px; color: #94a3b8;">&copy; 2025 HelseMed Care Norway. All rights reserved.</p>
    </div>
"""

# --- 1. PATIENT CONFIRMATION EMAIL ---
def send_confirmation_email(to_email: str, booking_id: str, patient_name: str, date: str, time: str, service: str):
    subject = f"Your Appointment is Confirmed – HelseMed Care Norway"
    
    body = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7fa;">
        <div style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <!-- Header -->
            <div style="background-color: #817bf4; padding: 30px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 24px;">Appointment Confirmed</h2>
                <p style="color: #e0e7ff; margin: 8px 0 0 0; font-size: 14px;">Booking Reference: {booking_id}</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px 24px; color: #334155;">
                <p style="font-size: 16px; margin-top: 0; line-height: 1.5;">Dear <strong>{patient_name}</strong>,</p>
                <p style="line-height: 1.5;">Your appointment has been successfully booked. We look forward to welcoming you to our clinic.</p>
                
                <!-- Details Table -->
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 24px 0; border: 1px solid #e2e8f0;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; width: 35%; color: #64748b; font-weight: 600; font-size: 14px; vertical-align: top;">Booking ID:</td>
                            <td style="padding: 8px 0; width: 65%; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right;">{booking_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; vertical-align: top; border-top: 1px dashed #e2e8f0;">Date:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; vertical-align: top; border-top: 1px dashed #e2e8f0;">Time:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{time}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; vertical-align: top; border-top: 1px dashed #e2e8f0;">Service:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{service}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 4px; font-size: 13px; color: #1e3a8a; line-height: 1.5;">
                    <strong>Please arrive 10–15 minutes earlier.</strong><br>
                    If you need to reschedule or cancel, simply reply to this email or call us at <strong>+47-94080888</strong>.
                </div>
            </div>

            <!-- Footer -->
            {EMAIL_FOOTER}
        </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, body)

# --- 2. ADMIN CONFIRMATION EMAIL ---
def send_admin_confirmation_email(booking_id: str, patient_name: str, patient_phone: str, patient_email: str, date: str, time: str, service: str):
    subject = f"🏥 New Appointment Booked — {patient_name}"
    
    body = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7fa;">
        <div style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            
            <!-- Header -->
            <div style="background-color: #1e293b; padding: 30px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 22px;">New Appointment Booked</h2>
                <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 14px;">ID: {booking_id}</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px 24px; color: #334155;">
                <p style="font-size: 16px; margin-top: 0; font-weight: bold;">System Alert:</p>
                <p style="margin-bottom: 24px;">A new appointment has been scheduled.</p>
                
                <!-- Details Table -->
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                        <!-- Patient Section -->
                        <tr>
                            <td style="padding: 8px 0; width: 35%; color: #64748b; font-weight: 600; font-size: 14px;">Patient Name:</td>
                            <td style="padding: 8px 0; width: 65%; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right;">{patient_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 1px dashed #e2e8f0;">Phone:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{patient_phone}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 1px dashed #e2e8f0;">Email:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{patient_email}</td>
                        </tr>
                        
                        <!-- Divider Row -->
                        <tr><td colspan="2" style="padding: 15px 0;"></td></tr>

                        <!-- Booking Section -->
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 2px solid #e2e8f0;">Booking ID:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 2px solid #e2e8f0;">{booking_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 1px dashed #e2e8f0;">Date:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 1px dashed #e2e8f0;">Time:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{time}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748b; font-weight: 600; font-size: 14px; border-top: 1px dashed #e2e8f0;">Service:</td>
                            <td style="padding: 8px 0; color: #1e293b; font-weight: 600; font-size: 14px; text-align: right; border-top: 1px dashed #e2e8f0;">{service}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 24px;">
                    <a href="#" style="background-color: #1e293b; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block;">Open Admin Panel</a>
                </div>
            </div>

            <!-- Footer -->
            {EMAIL_FOOTER}
        </div>
    </body>
    </html>
    """
    return _send_email(ADMIN_EMAIL, subject, body)

# --- 3. CANCELLATION EMAIL ---
def send_cancellation_email(to_email: str, patient_name: str, date: str, time: str, reason: str):
    subject = "Appointment Cancelled – HelseMed Care Norway"
    
    body = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7fa;">
        <div style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="background-color: #EF4444; padding: 30px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 24px;">Appointment Cancelled</h2>
            </div>
            
            <div style="padding: 32px 24px; color: #334155;">
                <p style="font-size: 16px; margin-top: 0;">Dear <strong>{patient_name}</strong>,</p>
                <p>We regret to inform you that your appointment scheduled for <strong>{date}</strong> at <strong>{time}</strong> has been cancelled.</p>
                
                <div style="background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 0; color: #991B1B; font-size: 13px; font-weight: bold;">Reason provided:</p>
                    <p style="margin: 4px 0 0 0; color: #7F1D1D; font-style: italic;">"{reason}"</p>
                </div>

                <p style="font-size: 14px; color: #64748b;">If you believe this is an error or wish to reschedule, please contact us immediately.</p>
            </div>
            {EMAIL_FOOTER}
        </div>
    </body>
    </html>
    """
    return _send_email(to_email, subject, body)