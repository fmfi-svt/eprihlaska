from flask_bootstrap.nav import BootstrapRenderer
from dominate import tags
from flask import url_for, session

from .consts import MENU

class ePrihlaskaNavRenderer(BootstrapRenderer):

    def __init__(self, **kwargs):
        self.MENU_URL_TO_NEXT_ENDPOINT = {}

        prev_endpoint = None
        for _, endpoint in MENU:
            url = url_for(endpoint)
            self.MENU_URL_TO_NEXT_ENDPOINT[url] = prev_endpoint
            prev_endpoint = endpoint
        super().__init__(**kwargs)

    def visit_View(self, node):

        item = tags.li()
        url = node.get_url()
        endpoint = self.MENU_URL_TO_NEXT_ENDPOINT.get(url, None)

        if endpoint and endpoint not in session:
            url = '#'

        item.add(tags.a(node.text, href=url))
        if node.active:
            item['class'] = 'active'
        return item
