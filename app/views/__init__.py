from .custom import home, dashboard

from .remittance import (
    remittance,
    remittance_sale,
    remittance_csv,
    remittance_sale_csv,
    remittance_active,
    remittance_remit,
    remittance_close,
    RemittanceDetail,
    RemittanceEdit,
    RemittanceSaleReport,
)

from .user import CustomerAutocomplete

from .sale import (
    sale,
    sale_csv,
    SaleCreate,
    SaleDetail,
    SaleUpdate,
    SaleDelete,
    SalePayment,
    sale_change_status,
)

from .order import order, order_csv, OrderCreate, OrderUpdate, OrderDelete

from .product import product, product_csv, ProductAutocomplete, ProductAllAutocomplete

from .price import product_price
from .adjustment import product_adjustment


from .cut_off import (
    cut_off,
    CutOffCreate,
    CutOffDetail,
    CutOffDelete,
    cut_off_close,
    cut_off_open,
)

from .collection import CollectionCreate, CollectionDelete

from .supplier import SupplierAutocomplete

from .procurement import (
    ProcurementDetail,
    procurement,
    procurement_csv,
    ProcurementCreate,
    ProcurementDetail,
    ProcurementUpdate,
    ProcurementDelete,
    procurement_open,
    procurement_close,
)

from .purchase import PurchaseCreate, PurchaseUpdate, PurchaseDelete
