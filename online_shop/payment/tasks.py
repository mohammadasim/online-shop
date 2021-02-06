from io import BytesIO
from celery import task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order

@task
def payment_completed(order_id):
    """
    Task to send an email notification when an order is
    successfully created
    :param order_id:
    :return:
    """
    order = Order.objects.get(id=order_id)
    # create
    subject = f'Online Shop - EE Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject=subject,
                         body=message,
                         from_email='admin@onlineshop.com',
                         to=[order.email])
    # generate pdf
    html = render_to_string('order/pdf.html', {'order': order})
    # create an instance of BytesIO, which is an in memory bytes buffer.
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')]
    # We write the pdf into bytesIO buffer
    weasyprint.HTML(string=html).write_pdf(out,
                                           stylesheets=stylesheets)

    # attach pds file
    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')
    # send email
    email.send()