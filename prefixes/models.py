import math
from crequest.middleware import CrequestMiddleware
from django.db import models
from django.utils import timezone

from audit.models import Log
from service import Service
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from products.models.product import Product
from django.db.models.signals import post_save
from django.dispatch import receiver


class PrefixStatus(models.Model):
    name = models.CharField(max_length=20, unique=True)
    is_suspended = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Prefix statuses'

    def __str__(self):
        return f'{self.name}'


class CompanyModelsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def check_instance(self, instance):
        result = isinstance(instance, self.model)
        if not result:
            raise ValueError('%s is not of type %s' % (instance, self.model._meta.object_name))
        return True

    def fetch_member_organisation(self, user, **kwargs):
        member_organisation = None
        if user:
            member_organisation = user.profile.member_organisation
        if (user is None) or (member_organisation is None):
            member_organisation = kwargs.get('member_organisation', None)
        return member_organisation

    def fetch_company_organisation(self, user, **kwargs):
        company_organisation = None
        if user:
            company_organisation = user.profile.company_organisation
        if (user is None) or (company_organisation is None):
            company_organisation = kwargs.get('company_organisation', None)
        return company_organisation

    def create(self, user=None, **kwargs):
        kwargs_copy = kwargs.copy()
        if user:
            member_organisation = self.fetch_member_organisation(user, **kwargs)
            company_organisation = self.fetch_company_organisation(user, **kwargs)
            kwargs_copy.update({'member_organisation': member_organisation,
                                'company_organisation': company_organisation})
        record = self.model(**kwargs_copy)
        record.save()
        return record

    def save(self, instance, user=None):
        self.check_instance(instance)
        if user:
            company_organisation = self.fetch_company_organisation(user)
            if instance.company_organisation != company_organisation:
                raise ValueError('User %s try to save %s not belong to him' % (user, instance))
        instance.save()
        return instance

    def delete(self, instance, user=None):
        self.check_instance(instance)
        if user:
            company_organisation = self.fetch_company_organisation(user)
            if instance.company_organisation != company_organisation:
                raise ValueError('User %s try to delete %s not belong to him' % (user, instance))
        instance.delete()

    def find(self, user=None, **query):
        """
        Returns a list of instances of the service's model filtered by the
        specified key word arguments.
        :param user: logged user to get member_organisation and company_organisation
        :param **query: filter parameters
        """
        if user:
            company_organisation = self.fetch_company_organisation(user, **query)
            res = self.model.objects.filter(company_organisation=company_organisation).filter(**query)
        else:
            return None

        return res

    def all(self, user=None):
        return self.find(user)

    def find_item(self, user=None, **query):
        try:
            res = self.find(user, **query).first()
        except Exception as e:
            return None
        return res


class ServiceManager(CompanyModelsManager):
    def save(self, prefix, user=None):
        return super().save(prefix, user)

    def make_active(self, prefix, user):
        prefix = Prefix.objects.get(prefix=prefix)
        user.profile.product_active_prefix = prefix
        user.profile.save()

    def get_active(self, user=None):
        return user and user.profile.product_active_prefix

    def find_suspended(self, user):
        statuses = PrefixStatus.objects.filter(is_suspended=True)
        prefixes = Prefix.objects.filter(
            company_organisation=user.profile.company_organisation
        ).filter(status__in=statuses)

        return prefixes

    def find_transferred(self, user):
        statuses = PrefixStatus.objects.filter(is_transferred=True)
        prefixes = (Prefix.objects.filter(company_organisation=user.profile.company_organisation)
                                  .filter(status__in=statuses))
        return prefixes


class Prefix(models.Model):
    class Meta:
        verbose_name_plural = 'prefixes'

    ACTIVE = 1
    INACTIVE = 2
    EXPIRED = 3
    TRANSFERRED = 4
    SPLIT = 5
    FROZEN = 6

    prefix = models.CharField(max_length=12, unique=True, db_index=True)
    status = models.ForeignKey(PrefixStatus, null=True, on_delete=models.CASCADE)

    # is_active now in Profile.product_active_prefix
    # is_active = models.BooleanField(default=False)

    is_suspended = models.BooleanField(default=False)
    is_special = models.CharField(max_length=20, default='')

    # db.Enum('NULL', 'READ-ONLY', 'EACH-ONLY', 'PACK-ONLY', 'CASE-ONLY', 'PALLET-ONLY',
    #          name='prefix_special_status'), default='NULL')

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    starting_from = models.CharField(max_length=13, null=True)
    starting_from_gln = models.CharField(max_length=13, null=True)

    company_organisation = models.ForeignKey(CompanyOrganisation, null=True, on_delete=models.CASCADE)
    member_organisation = models.ForeignKey(MemberOrganisation, null=True, on_delete=models.PROTECT)
    description = models.CharField(max_length=100, default='')

    objects = models.Manager()
    service = ServiceManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_instance_dict = self.__dict__.copy()

    def __str__(self):
        return self.prefix

    def _getValid(self, nums):
        """
        Redeclared here due to cyclic import
        """
        if not nums: return None
        cd1 = nums[-1]
        meat = nums[0:-1][::-1]  # cut cd away, reverse string, since x3 always applays from right (BC)
        odds = sum(map(lambda i: int(i) * 3, list(meat[0::2])))
        evns = sum(map(lambda i: int(i), list(meat[1::2])))
        cd2 = str(10 - ((odds + evns) % 10))[-1]  # 0 if 10 or reminder
        return nums[0:-1] + cd2

    def _get_first_avail_serial(self, products, capacity):
        last_serial = 0
        last_digits = int(math.log10(capacity))
        if products.count():
            gtins = set([int(p.gtin[:-1][-last_digits:]) for p in products])
            avail = set(range(capacity))
            try:
                last_serial = sorted(avail.difference(gtins))[0]
            except Exception as e:
                raise Exception(
                    'There are no available numbers left in this range. All numbers have now been allocated.'
                    ' To licence an additional company prefix please go to the'
                    ' <a href="http://www.gs1ie.org/Members-Area">Members Area</a> of the GS1 Ireland website.')
        return last_serial

    def get_range(self):
        start = self._getValid('{0:0<13}'.format(self.prefix))
        end = self._getValid('{0:9<13}'.format(self.prefix))
        return start, end

    def get_capacity(self):
        return 10 ** (12 - len(self.prefix))

    def get_company_organisation(self):
        return self.company_organisation

    def get_member_organisation(self):
        return self.member_organisation

    def is_upc(self):
        return self.prefix.startswith("0")

    def get_available_gtins(self, products, len_only=False):
        avail_gtins = []
        last_digits = int(math.log10(self.get_capacity()))
        if len(products) > 0:
            gtins = set([int(p.gtin[:-1][-last_digits:]) for p in products])
            avail = set(range(self.get_capacity()))
            try:
                if len_only:
                    _avail_gtins = avail.difference(gtins)
                else:
                    _avail_gtins = sorted(avail.difference(gtins))
            except:
                raise Exception(
                    'There are no available numbers left in this range. All numbers have now been allocated.'
                    ' To licence an additional company prefix please go to the'
                    ' <a href="http://www.gs1ie.org/Members-Area">Members Area</a> of the GS1 Ireland website.')
        else:
            _avail_gtins = set(range(self.get_capacity()))
        if len_only:
            return len(_avail_gtins)
        for gtin in _avail_gtins:
            f = '{0:0%d}' % (12 - len(self.prefix))
            avail_gtins.append("0" + self._getValid(self.prefix + f.format(gtin) + "0"))
        return avail_gtins

    def get_available_glns(self, locations, len_only=False):
        avail_glns = []
        last_digits = int(math.log10(self.get_capacity()))
        if len(locations) > 0:
            glns = set([int(p.gln[:-1][-last_digits:]) for p in locations])
            avail = set(range(self.get_capacity()))
            try:
                if len_only:
                    _avail_glns = avail.difference(glns)
                else:
                    _avail_glns = sorted(avail.difference(glns))
            except:
                raise Exception(
                    'There are no available numbers left in this range. All numbers have now been allocated.'
                    ' To licence an additional company prefix please go to the'
                    ' <a href="http://www.gs1ie.org/Members-Area">Members Area</a> of the GS1 Ireland website.')
        else:
            _avail_glns = set(range(self.get_capacity()))
        if len_only:
            return len(_avail_glns)
        for gln in _avail_glns:
            f = '{0:0%d}' % (12 - len(self.prefix))
            avail_glns.append("0" + self._getValid(self.prefix + f.format(gln) + "0"))
        return avail_glns

    def make_starting_from(self):
        if len(self.prefix) == 12:
            starting_from = self._getValid(self.prefix + '0')  # single gtin allocation
        else:
            products = Product.objects.filter(gs1_company_prefix=self.prefix)
            fas = self._get_first_avail_serial(products, self.get_capacity())
            f = '{0:0%d}' % (12 - len(self.prefix))
            starting_from = self._getValid(self.prefix + f.format(fas) + '0')
        self.starting_from = starting_from

    def _find_available(self):
        tmp = self.starting_from
        serial = tmp[len(self.prefix):12]
        f = '{0:0%d}' % len(serial)

        # find available gtin, maybe some product were deleted, start looking from 000
        tmp_serial = f.format(0)
        while len(tmp_serial) <= len(serial):
            starting_from = self._getValid(self.prefix + tmp_serial + "0")
            like_products = Product.objects.filter(gtin__endswith=starting_from)
            if not like_products:
                self.starting_from = starting_from
                return True
            # generate next serial
            tmp_serial = f.format(int(tmp_serial) + 1)

        self.starting_from = None
        raise Exception('You have reached the end of this prefix range. Please set new starting number manually.')

    def increment_starting_from(self):
        if len(self.prefix) == 12:  # prefixes for single one-off gtins can not increment
            return False

        tmp = self.starting_from
        serial = tmp[len(self.prefix):12]
        f = '{0:0%d}' % len(serial)

        # generate next serial
        tmp_serial = f.format(int(serial) + 1)

        # maximum serial reached
        if len(tmp_serial) > len(serial):
            return self._find_available()

        # generating gtin with next serial
        starting_from = self._getValid(self.prefix + tmp_serial + "0")

        # check if gtin is allocated
        like_products = Product.objects.filter(gtin__endswith=starting_from)
        if like_products:
            return self._find_available()

        self.starting_from = starting_from
        return True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        original_status_id = self._original_instance_dict.get('status_id')

        if original_status_id and original_status_id != self.status_id:
            request = CrequestMiddleware.get_request()  # global request
            username = request.user.username if request else None
            ip_address = request.META.get('REMOTE_ADDR') if request else None
            Log.objects.create(
                logger='',
                level='info',
                trace='',
                msg=(f'Prefix {self} status is changed from '
                     f'{original_status_id} to {self.status_id}'),
                ip_address=ip_address,
                username=username,
                created_at=timezone.now(),
            )


@receiver(post_save, sender=Prefix)     # post_save have created arg, pre_save have no
def make_starting_from(sender, instance, created, **kwargs):
    if created:
        try:
            instance.make_starting_from()
            instance.starting_from_gln = instance.starting_from
            instance.save()
        except:
            pass
