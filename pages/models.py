from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Q

# Create your models here.

class PagePublishedManager(models.Manager):
    def get_query_set(self):
        return super(PagePublishedManager, self).get_query_set().filter(status=1)
    
class PageDraftsManager(models.Manager):
    def get_query_set(self):
        return super(PageDraftsManager, self).get_query_set().filter(status=0)

class Page(models.Model):
	"""A simple page model"""
	
	STATUSES = (
		(0, ('Draft')),
		(1, ('Published'))
	)

	title = models.CharField(max_length=50)
	slug = models.SlugField(unique=True)
	author = models.ForeignKey(User)
	content = models.TextField()
	
	parent = models.ForeignKey('self', related_name="children", blank=True, null=True)
	order = models.IntegerField(blank=True)
	
	creation_date = models.DateTimeField(editable=False, auto_now_add=True)
	publication_date = models.DateTimeField(editable=False, null=True)
	
	status = models.IntegerField(choices=STATUSES, default=1)
	template = models.CharField(max_length=100, null=True, blank=True)
	
	published = PagePublishedManager()
	drafts = PageDraftsManager()
	objects = models.Manager()
	
	def __unicode__(self):
		return '%s' % (self.title)
	
	class Meta:
		ordering = ['order']

	def save(self):
		self.slug = slugify(self.slug)
		if self.status == 1 and self.publication_date is None:
			from datetime import datetime
			self.publication_date = datetime.now()
		if not self.status:
			self.status = 0
			
		recalculate_order = False
		if not self.order:
			self.order=1
			recalculate_order = True
		super(Page, self).save()
		# not so proud of this code
		if recalculate_order:
			self.set_default_order()
			super(Page, self).save()

	@classmethod
	def get_status_code(cls, content_type):
		code = None
		for ct in Content.CONTENT_TYPE:
			if ct[1] == content_type:
				code = ct[0]
				break
		return code
		
	def set_default_order(self):
		max = 0
		siblings = self.siblings()
		if siblings.count():
			for sibling in siblings:
				if sibling.order >= max:
					max = sibling.order
			self.order = max+1
			
	def siblings_and_me(self):
		if self.parent:
			return Page.objects.filter(parent=self.parent)
		else:
			return Page.objects.filter(parent__isnull=True)
	
	def children(self):
		if self.parent:
			return None
		else:
			return Page.objects.filter(parent = self)
        
	def siblings(self):
		return self.siblings_and_me().exclude(pk=self.id)
        
	def is_first(self):
		return self.siblings_and_me().order_by('order')[0:1][0] == self
    
	def is_last(self):
		return self.siblings_and_me().order_by('-order')[0:1][0] == self
        
		
	def get_admin_url(self):
		return '/admin/pages/page/%d/' % self.id
        
	def get_absolute_url(self):
		url = "/%s/" % self.slug
		page = self
		while page.parent:
			url = "/%s%s" % (page.parent.slug,url)
			page = page.parent
		return url
		
	def get_template(self):
		"""get the template of this page if defined or None otherwise"""
		p = self
		while p:
			if not p:
				return 'base.html'
			if p.template:
				return p.template
		
	@classmethod
	def switch_node(cls, node1, node2):
		buffer = node1.order
		node1.order = node2.order
		node2.order = buffer
		node1.save()
		node2.save()

	def up(self):
		sibling = self.siblings().order_by('-order').filter(order__lt=self.order+1)[0:1]
		if not sibling.count():
			return False
		if sibling[0].order == self.order:
			self.set_default_order()
			self.save()
		Page.switch_node(self, sibling[0])
		return True
        
	def down(self):
		sibling = self.siblings().order_by('order').filter(order__gt=self.order-1)[0:1]
		if not sibling.count():
			return False
		sibling = sibling[0]
		if sibling.order == self.order:
			sibling.set_default_order()
			sibling.save()
		Page.switch_node(self, sibling)
		return True