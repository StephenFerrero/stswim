from django.db import models

# Create your models here.

INVOICE_STATUS = (
    ('Open', 'Open'),
	('Sent', 'Sent'),
	('Closed', 'Closed'),
	('Paid', 'Paid'),
)

PAYMENT_METHOD = (
    ('Check', 'Check'),
	('Cash', 'Cash'),
)

class Invoice(models.Model):
    status =  models.CharField(choices=INVOICE_STATUS, default='Open', max_length=30)
    number = models.IntegerField()
	date = models.DateField()
	due_date = models.DateField()
	contact = models.ForeignKey(stswim.schedule.Parent, null=True, blank=True)
	
class Payment(models.Model):
	date = models.DateField()
	amount = models.IntegerField()
	method = models.CharField(choices=PAYMENT_METHOD, default='Check', max_length=30)
	check_number = models.IntegerField()

