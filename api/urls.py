from django.urls import path

from api.views import barcode_views
from .views import account_views
from .views import company_views
from .views import gpc_views
from .views import language_views
from .views import mo_views
from .views import prefix_views
from .views import product_views
from .views import user_views
from .views import subproduct_views

app_name = 'api'
urlpatterns = [
    # path('auth/', include('knox.urls')),
    path('register/',
         account_views.AccountCreateAPIView.as_view(),
         name='register'),
    path('accounts/login/',
         account_views.UserLoginView.as_view(),
         name='login'),
    path('accounts/renew/',
         account_views.UserRenewView.as_view(),
         name='renew'),
    path('accounts/logout/',
         account_views.UserLogoutView.as_view(),
         name='logout'),
    path('accounts/terms/',
         account_views.TermsOfServiceAPI.as_view(),
         name='terms'),
    path('accounts/logout_all/',
         account_views.UserLogoutAllView.as_view(),
         name='logout-all'),
    path('accounts/info/',
         account_views.CurrentUserInfo.as_view(),
         name='user-info'),

    path('accounts/profile/<str:username>',
         account_views.UserProfileView.as_view(),
         name='user_profile'),

    path('accounts/protected_data/',
         account_views.ProtectedDataView.as_view(),
         name='protected-data'),

    # users - list
    path('users/',
         user_views.UsersListCreateAPIView.as_view(),
         name='user-list'),
    # user - get details
    path('users/<str:profile__uid>/',
         user_views.UserRetreiveAPIView.as_view(),
         name='user-detail'),
    # user - get details
    path('users/<int:user_id>/update',
         user_views.UserUpdateAPIView.as_view(),
         name='user-update'),
    # upload prefixes
    path('users/upload/<str:mo>/',
         user_views.UserUploadAPIView.as_view(),
         name='user-upload'),

    # mo - get details
    path('member_organisations/<str:slug>/',
         mo_views.MemberOrganisationRetrieveAPIView.as_view(),
         name='mo-detail'),

    # companies - list
    path('companies/',
         company_views.CompaniesListCreateAPIView.as_view(),
         name='company-list'),
    # company - get details
    path('companies/<str:uuid>/',
         company_views.CompanyRetreiveAPIView.as_view(),
         name='company-detail'),
    # upload companies
    path('companies/upload/<str:mo>/',
         company_views.CompaniesUploadAPIView.as_view(),
         name='company-upload'),

    # create prefix
    path('companies/<str:uuid>/prefixes/',
         prefix_views.PrefixesListCreateAPIView.as_view(),
         name='prefix-create'),
    # create user
    path('companies/<str:uuid>/users/',
         user_views.UserCreateByCompanyAPIView.as_view(),
         name='user-create'),
    # create product
    path('prefixes/<str:prefix>/products',
         product_views.ProductWithPrefixListCreateAPIView.as_view(),
         name='products-with-prefix'),

    # prefixes - list
    path('prefixes/',
         prefix_views.PrefixesListCreateAPIView.as_view(),
         name='prefixes-list'),
    # prefix - get details
    path('prefixes/<str:prefix>/',
         prefix_views.PrefixesRetrieveAPIView.as_view(),
         name='prefixes-detail'),
    # upload prefixes
    path('prefixes/upload/<str:mo>/',
         prefix_views.PrefixesUploadAPIView.as_view(),
         name='prefixes-upload'),
    # for now only statuses are affected
    path('prefixes/<str:prefix>/<str:action>',
         prefix_views.PrefixModifyAPIView.as_view(),
         name='prefix-modify'),

    path('defaults/',
         product_views.ProductDefaultsListAPIView.as_view(),
         name='defaults-list'
         ),

    path('products/',
         product_views.ProductsListCreateAPIView.as_view(),
         name='product-list'),
    path('products/clone/',
         product_views.ProductCloneAPIView.as_view(),
         name='product-clone'),
    path('products/<str:gtin>/',
         product_views.ProductRetrieveAPIView.as_view(),
         name='product-detail'),

    path('products/create/subproducts/',
         subproduct_views.SubproductCreateListAPIView.as_view(),
         name='product-create-subproducts'),
    path('products/<str:gtin>/subproducts/',
         subproduct_views.SubproductListAPIView.as_view(),
         name='product-subproducts-list'),
    path('products/<str:product>/subproducts/<str:sub_product>/',
         subproduct_views.SubproductRetrieveAPIView.as_view(),
         name='product-subproducts-details'),

    path('templates/',
         product_views.ProductTemplateListAPIView.as_view(),
         name='templates-list'),
    path('templates/<str:id>/',
         product_views.ProductTemplateRetrieveAPIView.as_view(),
         name='templates-detail'),

    path('packaging/',
         product_views.ProductPackagingListAPIView.as_view(),
         name='packaging-list'),

    path('gpc/',
         gpc_views.GPCListAPIView.as_view(),
         name='gpc-list'),

    path('languages/',
         language_views.LanguageListAPIView.as_view(),
         name='languages-list'),
    path('ui-languages/',
         language_views.LanguageUIListAPIView.as_view(),
         name='ui-languages-list'),
    path('countries_of_origin/',
         language_views.COOListAPIView.as_view(),
         name='countries-list'),
    path('target_markets/',
         language_views.TMListAPIView.as_view(),
         name='target-market-list'),

    path('dimensions_uom/',
         language_views.ProductDimensionUOMView.as_view(),
         name='dimensions-uom'),
    path('weights_uom/',
         language_views.ProductWeightsUOMView.as_view(),
         name='weights-uom'),
    path('net_content_uom/',
         language_views.ProductNetContentUOMView.as_view(),
         name='net-content-uom'),

    path('barcodes/<str:gtin>/<slug:type>/',
         barcode_views.BarcodeListCreateAPIView.as_view(),
         name='barcodes'),

    path('barcodes/labels/',
         barcode_views.BarcodeLabelListAPIView.as_view(),
         name='barcodes-labels'),
]
