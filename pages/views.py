from models import *
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response

# Create your views here.

def details(request, full_slug):
	template = None
	slugs = full_slug.split('/')
	page_slug = slugs[-1]
	
	try:
		p = Page.published.get(slug = page_slug)
	except Page.DoesNotExist:
		raise Http404
		
	if not p.get_absolute_url().strip('/') == full_slug:
		raise Http404

	if not template:
		from stswim import settings
		template = settings.DEFAULT_PAGE_TEMPLATE
	return render_to_response(template, {'page_id' : p.id, 'page_slug' : p.slug, 'page_title' : p.title, 'page_content' : p.content})