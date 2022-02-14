from django.urls import path
import app.views as views

urlpatterns = [
    # remittance
    path("remittance", views.remittance, name="remittance"),
    path(
        "remittance/csv",
        views.remittance_csv,
        name="remittance-csv",
    ),
    path("remittance/active", views.remittance_active, name="remittance-active"),
    path("remittance/<int:pk>/remit", views.remittance_remit, name="remittance-remit"),
    path(
        "remittance/<int:pk>",
        views.RemittanceDetail.as_view(),
        name="remittance-detail",
    ),
    path(
        "remittance/<int:pk>/edit",
        views.RemittanceEdit.as_view(),
        name="remittance-edit",
    ),
    path("remittance/<int:pk>/close", views.remittance_close, name="remittance-close"),
    path("remittance/<int:pk>/sale", views.remittance_sale, name="remittance-sale"),
    path(
        "remittance/<int:pk>/sale/csv",
        views.remittance_sale_csv,
        name="remittance-sale-csv",
    ),
    # TODO: put the button in RemittanceDetail or not?
    path(
        "remittance/<int:pk>/sale/report",
        views.RemittanceSaleReport.as_view(),
        name="remittance-sale-report",
    ),
    # user
    path(
        "customer-autocomplete",
        views.CustomerAutocomplete.as_view(),
        name="customer-autocomplete",
    ),
    # sale
    path("sale", views.sale, name="sale"),
    path("sale/csv", views.sale_csv, name="sale-csv"),
    path("<int:pk>/sale/create", views.SaleCreate.as_view(), name="sale-create"),
    path("sale/<int:pk>", views.SaleDetail.as_view(), name="sale-detail"),
    path("sale/<int:pk>/update", views.SaleUpdate.as_view(), name="sale-update"),
    path("sale/<int:pk>/delete", views.SaleDelete.as_view(), name="sale-delete"),
    path("sale/<int:pk>/payment", views.SalePayment.as_view(), name="sale-payment"),
    path(
        "sale/<int:pk>/change/status",
        views.sale_change_status,
        name="sale-change-status",
    ),
    # path("sale/<int:pk>/cancel", views.cancel, name="sale-cancel"),
    # order
    path("order", views.order, name="order"),
    path("order/csv", views.order_csv, name="order-csv"),
    path("<int:pk>/order/create", views.OrderCreate.as_view(), name="order-create"),
    path("order/<int:pk>/update", views.OrderUpdate.as_view(), name="order-update"),
    path("order/<int:pk>/delete", views.OrderDelete.as_view(), name="order-delete"),
    # product
    path("product", views.product, name="product"),
    path("product/csv", views.product_csv, name="product-csv"),
    path("product/<int:pk>/price", views.product_price, name="product-price"),
    path(
        "product/<int:pk>/adjustment",
        views.product_adjustment,
        name="product-adjustment",
    ),
    path(
        "product-autocomplete",
        views.ProductAutocomplete.as_view(),
        name="product-autocomplete",
    ),
    path(
        "product-all-autocomplete",
        views.ProductAllAutocomplete.as_view(),
        name="product-all-autocomplete",
    ),
    # cut-off
    path("cut-off", views.cut_off, name="cut-off"),
    path("cut-off/create/", views.CutOffCreate.as_view(), name="cut-off-create"),
    path("cut-off/<int:pk>", views.CutOffDetail.as_view(), name="cut-off-detail"),
    path("cut-off/<int:pk>/open/", views.cut_off_open, name="cut-off-open"),
    path("cut-off/<int:pk>/close/", views.cut_off_close, name="cut-off-close"),
    path(
        "cut-off/<int:pk>/delete/", views.CutOffDelete.as_view(), name="cut-off-delete"
    ),
    # collection
    path(
        "collection/<int:cut_off_id>/<int:customer_id>/create/",
        views.CollectionCreate.as_view(),
        name="collection-create",
    ),
    path(
        "collection/<int:pk>/delete/",
        views.CollectionDelete.as_view(),
        name="collection-delete",
    ),
    path(
        "supplier-autocomplete",
        views.SupplierAutocomplete.as_view(create_field="name"),
        name="supplier-autocomplete",
    ),
    path("procurement", views.procurement, name="procurement"),
    path("procurement/csv", views.procurement_csv, name="procurement-csv"),
    path(
        "procurement/create/",
        views.ProcurementCreate.as_view(),
        name="procurement-create",
    ),
    path(
        "procurement/<int:pk>",
        views.ProcurementDetail.as_view(),
        name="procurement-detail",
    ),
    path(
        "procurement/<int:pk>/update/",
        views.ProcurementUpdate.as_view(),
        name="procurement-update",
    ),
    path(
        "procurement/<int:pk>/delete/",
        views.ProcurementDelete.as_view(),
        name="procurement-delete",
    ),
    path("procurement/<int:pk>/open/", views.procurement_open, name="procurement-open"),
    path(
        "procurement/<int:pk>/close/", views.procurement_close, name="procurement-close"
    ),
    path(
        "procurement/<int:pk>/purchase/create/",
        views.PurchaseCreate.as_view(),
        name="purchase-create",
    ),
    path(
        "procurement/purchase/<int:pk>/update/",
        views.PurchaseUpdate.as_view(),
        name="purchase-update",
    ),
    path(
        "procurement/purchase/<int:pk>/delete/",
        views.PurchaseDelete.as_view(),
        name="purchase-delete",
    ),
    #    TODO: Replace this with account/profile
    path("", views.home, name="home"),
]
