import csv
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import get_object_or_404, redirect, render
from app.models import Product
import django_filters
from django.http.response import Http404, HttpResponse


class ProductFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(ProductFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ["category", "name", "is_active"]


def product(request):
    filter = ProductFilter(request.GET, queryset=Product.objects.all())
    products = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))

    paginator = Paginator(products, 10)

    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "filter": filter,
        "has_filter": has_filter,
        "stock": "I",
    }
    return render(request, "app/product.html", context)


@permission_required("products.can_access_inventory")
def product_csv(request):
    filter = ProductFilter(request.GET, queryset=Product.objects.all())
    products = filter.qs
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)
    writer.writerow(
        [
            "PRODUCT",
            "PRICE",
            "QUANTITY",
            "AMOUNT",
        ]
    )
    for product in products:

        writer.writerow(
            [product, product.price, product.inventory, product.inventory_amount]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Inventory - {str(datetime.date.today())}.csv"'
    return response


from django.db.models import Q
from dal import autocomplete


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, product):
        return f"{product} | {product.inventory} | {product.price}"

    def get_queryset(self):
        qs = Product.active.all()
        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) | Q(category__name__icontains=self.q)
            )
        return qs


class ProductAllAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
