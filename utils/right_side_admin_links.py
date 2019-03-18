from collections import namedtuple


__all__ = (
    'RightSideAdminLinkInfo',
    'RightSideLinksAdminMixin',
)

RightSideAdminLinkInfo = namedtuple('RightSideAdminLinkInfo', 'name url')


class RightSideLinksAdminMixin:

    def get_right_side_links(self, obj):
        if obj is None:
            return []

        prefix = (
            f'/member_organisations/memberorganisationowner/{self.url_prefix}'
            if getattr(self, 'url_prefix', False) else ''
        )

        links = [
            {
                'name': link.name,
                'url': '/admin{prefix}/{url}'.format(
                    prefix=prefix,
                    url=link.url.format(obj=obj)
                )
            }
            for link in getattr(self, 'right_side_links', [])
        ]
        return links


    def render_change_form(self,
                           request,
                           context,
                           add=False,
                           change=False,
                           form_url='',
                           obj=None):
        context.update(
            {'right_side_links': self.get_right_side_links(obj)}
        )
        return super().render_change_form(
            request, context, add, change, form_url, obj
        )
