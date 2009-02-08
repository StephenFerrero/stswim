from stswim.utils import auto_render
from stswim.pages.models import *
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _
from django import newforms as forms
from django.contrib.contenttypes.models import ContentType

@staff_member_required
@auto_render
def list_pages(request):
    pages = Page.objects.filter(parent__isnull=True)
    return 'pages/change_list.html', locals()

@staff_member_required
@auto_render
def up(request, hnode_id):
    node = Page.objects.get(pk=hnode_id)
    node.up()
    return HttpResponseRedirect("../../")

@staff_member_required
@auto_render
def down(request, hnode_id):
    node = Page.objects.get(pk=hnode_id)
    node.down()
    return HttpResponseRedirect("../../")
    