"""
Footer template tag.
"""

from datetime import datetime

from django import template
from django.conf import settings
from django.template import base, loader

register = template.Library()


class SiteFooterNode(template.Node):
    def render(self, context):
        data = getattr(settings, 'ADMIN_FOOTER_DATA', {
            'period': datetime.now().year
        })
        tpl = loader.get_template('site_footer/footer.html')
        return tpl.render(data)


@register.tag
def site_footer(parser, token):
    tag_name = token.split_contents()

    if len(tag_name) > 1:
        raise base.TemplateSyntaxError(
            '{} tag does not accept any argument(s): {}'.format(
                token.contents.split()[0],
                ', '.join(token.contents.split()[1:])
            ))

    return SiteFooterNode()
