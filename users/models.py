from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from prefixes.models import Prefix
from service import Service
from member_organisations.models import MemberOrganisation, ProductTemplate
from company_organisations.models import CompanyOrganisation


class Profile(models.Model):
    db_name = 'profile'

    uid = models.CharField(max_length=124, null=True, default='')
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    member_organisation = models.ForeignKey(MemberOrganisation, null=True, on_delete=models.CASCADE,)
    company_organisation = models.ForeignKey(
        CompanyOrganisation, null=True, on_delete=models.CASCADE
    )
    product_active_prefix = models.ForeignKey(
        Prefix, default=None, on_delete=models.SET_NULL, related_name='profiles',
        null=True, blank=True,
    )
    is_authenticated = True
    active = models.BooleanField(default=True)
    customer_role = models.CharField(max_length=20,  default='')

    # Terms and conditions agreement
    agreed = models.BooleanField(default=False)
    agreed_date = models.DateTimeField(default=timezone.now)
    agreed_version = models.CharField(max_length=30, null=True, default='')

    agreed_barcode_disclaimer = models.BooleanField(default=False)
    agreed_barcode_disclaimer_date = models.DateTimeField(default=timezone.now)

    login_count = models.IntegerField(null=True)

    language = models.CharField(max_length=2,  default='en')

    # Enable leading digit?
    enable_leading = models.BooleanField(default=False)

    # Show advanced tab?
    advanced_tab = models.BooleanField(default=False)

    def get_available_templates(self):
        return ProductTemplate.objects.filter(member_organisation=self.member_organisation)


@receiver(post_save, sender=AuthUser)
def create_user_profile(sender, instance, created, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    if profile:
        instance.profile.save()
    else:
        profile = Profile(user_id=instance.id)
        profile.save()


class UsersService(Service):
    def __init__(self):
        super().__init__(Profile)

    def get_or_create(self, email, defaults={}):
        # get or create user
        auth_user, auth_user_created = AuthUser.objects.get_or_create(
            email=email, defaults={'username': email}
        )

        update_profile = False

        # link user to the organisations
        member_organisation = defaults.get('member_organisation', None)
        if auth_user_created and member_organisation:
            if self.check_multiple_member_organisations(auth_user, member_organisation):
                raise ValidationError(
                    f'Multiple member organizations for the same user are not allowed'
                )

            member_organisation.add_user(auth_user)
            auth_user.profile.member_organisation = member_organisation
            update_profile = True

        company_organisation = defaults.get('company_organisation', None)
        if auth_user_created and company_organisation:
            if self.check_multiple_company_organisations(auth_user, company_organisation):
                raise ValidationError(
                    f'Multiple companies for the same user are not allowed'
                )

            company_organisation.add_user(auth_user)
            auth_user.profile.company_organisation = company_organisation
            if defaults.get('uid'):
                auth_user.profile.uid = defaults.get('uid')
            update_profile = True

        if update_profile:
            auth_user.profile.save()

        return auth_user, auth_user_created

    def get_no_create(self, email, defaults=None):
        auth_user = AuthUser.objects.get(email=email)
        return auth_user

    def update_details(self, auth_user, details):
        update_profile = False

        # link user to the organisations
        member_organisation = details.get('member_organisation', None)
        if member_organisation:
            if self.check_multiple_member_organisations(auth_user, member_organisation):
                raise ValidationError(
                    f'Multiple member organizations for the same user are not allowed'
                )

            member_organisation.get_or_add_user(auth_user)
            auth_user.profile.member_organisation = member_organisation
            update_profile = True

        company_organisation = details.get('company_organisation', None)
        if company_organisation:
            if self.check_multiple_company_organisations(auth_user, company_organisation):
                raise ValidationError(f'Multiple companies for the same user are not allowed')

            company_organisation.get_or_add_user(auth_user)
            auth_user.profile.company_organisation = company_organisation
            if details.get('uid'):
                auth_user.profile.uid = details.get('uid')
            update_profile = True

        if update_profile:
            auth_user.profile.save()

        return auth_user

    def create(self, email, defaults=None):
        defaults = defaults or {}

        member_organisation = defaults.pop('member_organisation', None)

        company_organisation = defaults.pop('company_organisation', None)

        uid = defaults.pop('uid', None)

        auth_user = AuthUser.objects.create(email=email, **defaults)

        update_profile = False

        # link user to the organisations
        if member_organisation:
            member_organisation.add_user(auth_user)
            auth_user.profile.member_organisation = member_organisation
            update_profile = True

        if company_organisation:
            company_organisation.add_user(auth_user)
            auth_user.profile.company_organisation = company_organisation
            update_profile = True

        if uid:
            auth_user.profile.uid = uid
            update_profile = True

        if update_profile:
            auth_user.profile.save()

        return auth_user

    def get_company_organisation(self, user):
        company_organisation = user.company_organisations_companyorganisation.first()
        return company_organisation

    @staticmethod
    def check_multiple_company_organisations(user, company_organisation=None):
        """
        Detect if a user has more than one company organisation
        """

        company_organisations = user.company_organisations_companyorganisation.all()

        if company_organisation:
            company_organisations = company_organisations.exclude(
                pk=company_organisation.pk
            )

        return company_organisations.exists()

    @staticmethod
    def check_multiple_member_organisations(user, company_organisation=None):
        """
        Detect if a user has more than one member organisation
        """

        member_organisations = user.member_organisations_memberorganisation.all()

        if company_organisation:
            member_organisations = member_organisations.exclude(
                pk=company_organisation.pk
            )
        return member_organisations.exists()

    def find(self, **kwargs):
        auth_user = AuthUser.objects.filter(email=kwargs['email']).first()
        #res = User.objects.filter(user=auth_user, customer_role=kwargs['customer_role'])
        #if res:
        return auth_user

    def get(self, user, field):
        try:
            value = user.__getattribute__(field)
        except:
            try:
                value = user.profile.__getattribute__(field)
            except:
                value = None
        return value
