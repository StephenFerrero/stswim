from django.contrib import admin
from stswim.pages.models import Page

class Page(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('title')}
	radio_fields = {'status': admin.VERTICAL}

