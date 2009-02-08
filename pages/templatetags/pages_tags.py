from django import template
from stswim.pages.models import Page

register = template.Library()

@register.inclusion_tag('menu.html', takes_context=True)
def show_menu(context, page_id):
	page = Page.objects.get(id=page_id)
	context['page'] = page
	if page.parent:
		children = page.siblings_and_me()
		parent = page.parent
		context['parent'] = parent
		context['children'] = children
	else:
		children = Page.objects.filter(parent = page)
		parent = page
		context['parent'] = parent
		context['children'] = children
	return context



@register.inclusion_tag('pages/admin_menu.html', takes_context=True)
def show_admin_menu(context, page, url='/admin/pages/page/', level=None):
    children = page.children.all()
    request = context['request']
    if level is None:
        level = 0
    else:
        level = level+2
    return locals()

@register.filter(name='truncateletters')
def truncateletters(value, arg):
    """
    Truncates a string after a certain number of letters

    Argument: Number of letters to truncate after
    """
    def truncate_letters(s, num):
        "Truncates a string after a certain number of letters."
        length = int(num)
        letters = [l for l in s]
        if len(letters) > length:
            letters = letters[:length]
            if not letters[-3:] == ['.','.','.']:
                letters += ['.','.','.']
        return ''.join(letters)

    try:
        length = int(arg)
    except ValueError: # invalid literal for int()
        return value # Fail silently
    if not isinstance(value, basestring):
        value = str(value)
    return truncate_letters(value, length)