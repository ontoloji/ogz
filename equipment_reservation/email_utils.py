from flask import render_template_string
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f'Failed to send email: {str(e)}')


def send_email(app, subject, recipient, text_body, html_body=None):
    """Send email with both text and HTML body"""
    msg = Message(subject, recipients=[recipient])
    msg.body = text_body
    if html_body:
        msg.html = html_body

    # Send email in background thread
    Thread(target=send_async_email, args=(app, msg)).start()


def send_reservation_confirmation(app, reservation):
    """Send reservation confirmation email"""
    subject = f'Rezervasyon Onayı - {reservation.equipment.name}'

    text_body = f'''
Merhaba {reservation.user.full_name or reservation.user.username},

Rezervasyonunuz onaylanmıştır.

Ekipman: {reservation.equipment.name}
Başlangıç: {reservation.start_time.strftime('%d/%m/%Y %H:%M')}
Bitiş: {reservation.end_time.strftime('%d/%m/%Y %H:%M')}
Amaç: {reservation.purpose or 'Belirtilmemiş'}

İyi çalışmalar!
'''

    html_body = f'''
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 10px;">
            Rezervasyon Onayı
        </h2>
        <p>Merhaba <strong>{reservation.user.full_name or reservation.user.username}</strong>,</p>
        <p>Rezervasyonunuz onaylanmıştır.</p>

        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 5px;"><strong>Ekipman:</strong></td>
                    <td style="padding: 5px;">{reservation.equipment.name}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Başlangıç:</strong></td>
                    <td style="padding: 5px;">{reservation.start_time.strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Bitiş:</strong></td>
                    <td style="padding: 5px;">{reservation.end_time.strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Amaç:</strong></td>
                    <td style="padding: 5px;">{reservation.purpose or 'Belirtilmemiş'}</td>
                </tr>
            </table>
        </div>

        <p style="color: #28a745;">İyi çalışmalar!</p>
    </div>
</body>
</html>
'''

    send_email(app, subject, reservation.user.email, text_body, html_body)


def send_reservation_cancellation(app, reservation):
    """Send reservation cancellation email"""
    subject = f'Rezervasyon İptali - {reservation.equipment.name}'

    text_body = f'''
Merhaba {reservation.user.full_name or reservation.user.username},

Rezervasyonunuz iptal edilmiştir.

Ekipman: {reservation.equipment.name}
Başlangıç: {reservation.start_time.strftime('%d/%m/%Y %H:%M')}
Bitiş: {reservation.end_time.strftime('%d/%m/%Y %H:%M')}
'''

    html_body = f'''
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 10px;">
            Rezervasyon İptali
        </h2>
        <p>Merhaba <strong>{reservation.user.full_name or reservation.user.username}</strong>,</p>
        <p>Rezervasyonunuz iptal edilmiştir.</p>

        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 5px;"><strong>Ekipman:</strong></td>
                    <td style="padding: 5px;">{reservation.equipment.name}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Başlangıç:</strong></td>
                    <td style="padding: 5px;">{reservation.start_time.strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Bitiş:</strong></td>
                    <td style="padding: 5px;">{reservation.end_time.strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
'''

    send_email(app, subject, reservation.user.email, text_body, html_body)


def send_calibration_reminder(app, equipment, admin_emails):
    """Send calibration reminder to administrators"""
    subject = f'Kalibrasyon Hatırlatıcısı - {equipment.name}'

    text_body = f'''
Ekipman kalibrasyon tarihine yaklaşmıştır:

Ekipman: {equipment.name}
Tip: {equipment.equipment_type}
Seri No: {equipment.serial_number or 'Belirtilmemiş'}
Son Kalibrasyon: {equipment.last_calibration_date.strftime('%d/%m/%Y') if equipment.last_calibration_date else 'Belirtilmemiş'}
Sonraki Kalibrasyon: {equipment.next_calibration_date.strftime('%d/%m/%Y') if equipment.next_calibration_date else 'Belirtilmemiş'}

Lütfen kalibrasyon işlemini planlayın.
'''

    html_body = f'''
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #ffc107; border-bottom: 2px solid #ffc107; padding-bottom: 10px;">
            ⚠️ Kalibrasyon Hatırlatıcısı
        </h2>
        <p>Ekipman kalibrasyon tarihine yaklaşmıştır:</p>

        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 5px;"><strong>Ekipman:</strong></td>
                    <td style="padding: 5px;">{equipment.name}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Tip:</strong></td>
                    <td style="padding: 5px;">{equipment.equipment_type}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Seri No:</strong></td>
                    <td style="padding: 5px;">{equipment.serial_number or 'Belirtilmemiş'}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Son Kalibrasyon:</strong></td>
                    <td style="padding: 5px;">{equipment.last_calibration_date.strftime('%d/%m/%Y') if equipment.last_calibration_date else 'Belirtilmemiş'}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Sonraki Kalibrasyon:</strong></td>
                    <td style="padding: 5px;">{equipment.next_calibration_date.strftime('%d/%m/%Y') if equipment.next_calibration_date else 'Belirtilmemiş'}</td>
                </tr>
            </table>
        </div>

        <p style="color: #dc3545;"><strong>Lütfen kalibrasyon işlemini planlayın.</strong></p>
    </div>
</body>
</html>
'''

    for email in admin_emails:
        send_email(app, subject, email, text_body, html_body)
