from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('django.views.generic.simple',
		       
		       (r'^$', 'direct_to_template', {'template': 'main1col.html'}), #Catch root url to homepage
		       (r'^manage/$', 'redirect_to', {'url': '/schedule/manage/'}),
)

urlpatterns += patterns('',
		       # Example:
		       # (r'^stswim/', include('stswim.foo.urls')),
		   
		       #urls.py includes
		       (r'^accounts/', include('stswim.accounts.urls')),
		       (r'^schedule/', include('stswim.schedule.urls')),
			   (r'^register/$', 'stswim.schedule.views.regorlogin'),
		
			   (r'^login/$', 'stswim.schedule.views.regorlogin'),
			   (r'^logout/$', 'stswim.accounts.views.logout_view'),
		       
		       #Pages app admin urls
		       (r'^admin/pages/page/$', 'stswim.pages.admin_views.list_pages'),
		       (r'^admin/pages/page/(?P<hnode_id>\d+)/up/$', 'stswim.pages.admin_views.up'),
		       (r'^admin/pages/page/(?P<hnode_id>\d+)/down/$', 'stswim.pages.admin_views.down'),
		       
		       # Built-In Admin
		       (r'^admin/', include(admin.site.urls)),

		       # Handle static files
		       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/stephen/Projects/stswim/media/'}),
		       
		       #content pages
		       #(r'^(?P<page_slug>\w+)/$', 'pages.views.details'),
		       (r'^(?P<full_slug>(.*))/$', 'stswim.pages.views.details'),
			   
)


