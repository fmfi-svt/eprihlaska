from flask_bootstrap.nav import BootstrapRenderer, sha1
from flask_nav.elements import NavigationItem, View
from dominate import tags
from flask import url_for, session
from flask_login import current_user
from . import consts as c

from .consts import MENU

class UserGreeting(View):
    def __init__(self):
        self.url_for_kwargs = {}

    @property
    def endpoint(self):
        if hasattr(current_user, 'id'):
            return 'index'
        else:
            return 'signup'

    @property
    def text(self):
        if hasattr(current_user, 'id'):
            return c.WELCOME.format(current_user.email)
        else:
            return c.SIGNUP

class LogInLogOut(View):
    def __init__(self):
        self.url_for_kwargs = {}

    @property
    def endpoint(self):
        if hasattr(current_user, 'id'):
            return 'logout'
        else:
            return 'login'

    @property
    def text(self):
        if hasattr(current_user, 'id'):
            return c.LOGOUT
        else:
            return c.LOGIN

# Taken from
# https://gist.github.com/thedod/eafad9458190755ce943e7aa58355934
class ExtendedNavbar(NavigationItem):
    def __init__(self, title, root_class='navbar navbar-default', items=[], right_items=[]):
        self.title = title
        self.root_class = root_class
        self.items = items
        self.right_items = right_items

class ePrihlaskaNavRenderer(BootstrapRenderer):

    def __init__(self, **kwargs):
        self.MENU_URL_TO_NEXT_ENDPOINT = {}

        prev_endpoint = None
        for _, endpoint in MENU:
            url = url_for(endpoint)
            self.MENU_URL_TO_NEXT_ENDPOINT[url] = prev_endpoint
            prev_endpoint = endpoint
        super().__init__(**kwargs)

    # Taken from
    # https://gist.github.com/thedod/eafad9458190755ce943e7aa58355934
    def visit_ExtendedNavbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = node.root_class

        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-main'))
        for item in node.items:
            bar_list.add(self.visit(item))

        if node.right_items:
            right_bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))
            for item in node.right_items:
                right_bar_list.add(self.visit(item))

        return root

    def visit_View(self, node):

        item = tags.li()
        url = node.get_url()
        endpoint = self.MENU_URL_TO_NEXT_ENDPOINT.get(url, None)

        if endpoint and endpoint not in session:
            url = '#'

        # Endpoints which are allowed once the application has been submitted.
        #
        # Note that 'admissions_wavers' refers to the endpoint that preceeds
        # 'final' (which is what should only be allowed here).
        allowed_endpoints = [None, 'admissions_wavers']

        if 'application_submitted' in session \
           and endpoint not in allowed_endpoints:
            url = '#'

        item.add(tags.a(node.text, href=url))
        if node.active:
            item['class'] = 'active'
        return item
