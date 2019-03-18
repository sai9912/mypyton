from django.urls import path

from .views import products, subproducts, products_js

app_name = 'products'
urlpatterns = [
    path('', products.products_list, name='products_list'),

    path('js-list', products.products_list_js, name='products_list_js'),
    path('add/', products.add_product, name='add_product'),  # legacy
    path('js-add/', products_js.js_add_product, name='add_product_js'),  # vuejs

    path('add_product_package_type/', products.add_product_package_type, name='add_product_package_type'),
    path('add/details/', products.add_product_base_details, name='add_product_base_details'),
    path('subproduct/add/case/', subproducts.subproduct_add_case, name='subproduct_add_case'),
    path('subproduct/add/case/skip/', subproducts.subproduct_add_case_skip, name='subproduct_add_case_skip'),
    path('subproduct/add/case_edit/', subproducts.subproduct_add_case_edit, name='subproduct_add_case_edit'),
    path('subproduct/add/case_edit/skip/', subproducts.subproduct_add_case_edit_skip, name='subproduct_add_case_edit_skip'),
    path('subproduct/add/case_details/', subproducts.subproduct_add_case_details, name='subproduct_add_case_details'),
    path('add_product_select_arbitrary', subproducts.add_product_select_arbitrary, name='add_product_select_arbitrary'),

    path('<int:product_id>/fulledit/', products_js.fulledit_js, name='fulledit'),
    path('<int:product_id>/fulledit_js/', products_js.fulledit_js, name='fulledit_js'),
    path('<int:product_id>/fulledit_legacy/', products.fulledit, name='fulledit_legacy'),
    path('<int:product_id>/duplicate/<target_market>/', products.duplicate_product, name='duplicate_product'),
    path('<int:product_id>/delete/', products.delete_product, name='delete_product'),
    path('<int:product_id>/upload_image/', products.upload_image, name='upload_image'),
    path('<int:product_id>/print_summary/', products.product_print_summary, name='product_print_summary'),
    path('<int:product_id>/view_summary/', products.view_product_summary, name='view_product_summary'),
    path('<int:product_id>/delete_target_market/', products.delete_target_market, name='delete_target_market'),

    path('ajax/<int:product_id>/mark/', products.ajax_product_mark),
    path('ajax/<int:product_id>/unmark/', products.ajax_product_unmark),
    path('ajax/<int:product_id>/subproduct_select', subproducts.subproduct_ajax_select, name='subproduct_ajax_select'),
    path('ajax/<int:product_id>/subproduct_unselect', subproducts.subproduct_ajax_unselect, name='subproduct_ajax_unselect'),
    path('ajax/<int:product_id>/subproduct_edit', subproducts.ajax_subproduct_edit, name='ajax_subproduct_edit'),
    path('ajax/<int:product_id>/subproduct_add', subproducts.ajax_subproduct_add, name='ajax_subproduct_add'),
    path('ajax/<int:product_id>/subproducts_list', subproducts.ajax_subproducts_list, name='ajax_subproducts_list'),
    path('ajax/<int:product_id>/av_subproducts_list', subproducts.ajax_av_subproducts_list, name='ajax_av_subproducts_list'),
    path('ajax/subproduct_selected', subproducts.subproduct_ajax_selected, name='subproduct_ajax_selected'),
    path('ajax/get_subproducts_by_gtin/<slug:gtin>/', products_js.ajax_get_subproducts_by_gtin),

    path('ajax/<int:package_type_id>/package_type/', products.ajax_get_package_type, name='ajax_get_package_type'),
]
