from django import forms
from django.contrib import admin
from django.db import models

from member_organisations.admin_mixins import MemberOrganisationCustomMixin
from member_organisations.custom_admin.base_views import BaseM2MTokenAdmin
from member_organisations.custom_admin.mo_owner_admin import MemberOrganisationOwnerAdmin
from member_organisations.models import (
    MemberOrganisation,
    MemberOrganisationOwner,
    ProductTemplate,
    ProductAttribute,
    ProductPackaging,
    M2MToken,
    MemberOrganisationUser,
    MemberOrganisationRelation)
from products.models.product import Product


class MemberOrganisationAdmin(MemberOrganisationCustomMixin, admin.ModelAdmin):
    pass


class MemberOrganisationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'is_admin',)


class ProductAttributeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['path'].widget = forms.Select(choices=self.get_product_fields_choices())

    @staticmethod
    def get_product_fields_choices():
        concrete_model = Product._meta.concrete_model
        path_prefix = f'{concrete_model.__module__}.{concrete_model.__qualname__}'

        local_fields = [
            (f'{path_prefix}.{field.name}', f'{path_prefix}.{field.name}')
            for field in concrete_model._meta.local_fields
        ]
        m2m_fields = [
            (f'{path_prefix}.{field.name}', f'{path_prefix}.{field.name}')
            for field in concrete_model._meta.many_to_many
        ]

        return local_fields + m2m_fields


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'path', 'ui_mandatory', 'ui_enabled', 'ui_read_only', 'member_organisation',
    )
    list_filter = ('member_organisation',)
    form = ProductAttributeForm


class ProductAttributeInline(admin.TabularInline):
    model = ProductTemplate.attributes.through


class ProductTemplateAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order', 'package_level', 'member_organisation')
    inlines = (ProductAttributeInline,)
    exclude = ('attributes',)
    list_filter = ('member_organisation', 'package_level',)


class ProductPackagingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order', 'member_organisation')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 60})},
    }
    list_filter = ('member_organisation',)


class M2MTokenAdmin(BaseM2MTokenAdmin):
    list_display = ('id', 'description', 'user',)
    list_display_links = ('id', 'description',)
    readonly_fields = ('token',)


class MemberOrganisationRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(MemberOrganisationUser, MemberOrganisationUserAdmin)
admin.site.register(MemberOrganisationOwner, MemberOrganisationOwnerAdmin)
admin.site.register(MemberOrganisation, MemberOrganisationAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductTemplate, ProductTemplateAdmin)
admin.site.register(ProductPackaging, ProductPackagingAdmin)
admin.site.register(M2MToken, M2MTokenAdmin)
admin.site.register(MemberOrganisationRelation, MemberOrganisationRelationAdmin)
