from django import forms

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext as _

from member_organisations.models import MemberOrganisation, MemberOrganisationUser


def get_registration_type_choices():
    """
    If user selects MO, it will become MO admin (inactive).
    If user selects GO, it will become GO admin (inactive).
    """

    registration_choices = [
        (item.pk, f'MO Admin of {item}') for item in
        MemberOrganisation.objects.all().order_by('name')
    ]
    registration_choices.insert(0, ('go_admin', 'GO Admin'))
    return registration_choices


class StaffMemberRegistration(UserCreationForm):
    """
    GO/MO staff personal registration form
    """

    username = forms.EmailField(label=_('Email'), max_length=150)
    registration_type = forms.ChoiceField(
        # choices will be set in __init__,
        # cause migrations can't be performed if we touch models here
        label=_('Member Organisation'), choices=[]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_type'].choices = get_registration_type_choices()

    def save(self, commit=True):
        """
        Assign user groups, organisations, set is_active to False
        """

        user = super().save(True)  # we have to save to get pk for m2m adding
        user.is_active = False
        user.email = user.username  # checked by the field validation

        # detect which group to assign to the new user
        if self.cleaned_data['registration_type'] == 'go_admin':
            user.groups.add(Group.objects.get(name='GO Admins'))
        else:
            # MO admin must belong to the "MO Admins" group certain organization
            user.groups.add(Group.objects.get(name='MO Admins'))
            member_organisation = MemberOrganisation.objects.get(
                pk=self.cleaned_data['registration_type']
            )
            MemberOrganisationUser.objects.create(
                user=user, organization=member_organisation, is_admin=True
            )

        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ('username', )


class StaffMemberLogin(AuthenticationForm):
    """
    GO/MO staff personal login form
    """

    username = UsernameField(label=_('Email'), max_length=150)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Overridden base class method, added features:
            - case insensitive usernames
        """

        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user_model = get_user_model()

        if username is not None and password:
            user_instance = user_model.objects.filter(username__iexact=username.strip()).first()
            username = user_instance.username if user_instance else username
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                # An authentication backend may reject inactive users. Check
                # if the user exists and is inactive, and raise the 'inactive'
                # error if so.
                try:
                    self.user_cache = user_model._default_manager.get_by_natural_key(username)
                except user_model.DoesNotExist:
                    pass
                else:
                    self.confirm_login_allowed(self.user_cache)
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


