from django import http
from dal import autocomplete
from app.models.supplier import Supplier
from django.utils.translation import ugettext_lazy as _


class SupplierAutocomplete(autocomplete.Select2QuerySetView):
    def get_create_option(self, context, q):
        """Form the correct create_option to append to results."""
        create_option = []
        display_create_option = False
        if self.create_field and q:
            page_obj = context.get("page_obj", None)
            if page_obj is None or page_obj.number == 1:
                display_create_option = True

            # Don't offer to create a new option if a
            # case-insensitive) identical one already exists
            existing_options = (
                self.get_result_label(result).lower()
                for result in context["object_list"]
            )
            if q.lower() in existing_options:
                display_create_option = False
        if display_create_option:
            create_option = [
                {
                    "id": q,
                    "text": _('Create "%(new_value)s"') % {"new_value": q},
                    "create_id": True,
                }
            ]
        return create_option

    def post(self, request, *args, **kwargs):
        """Save new item when post was called and return a json response"""
        text = request.POST.get("text", None)
        if text is None:
            return http.HttpResponseBadRequest()
        supplier = Supplier.objects.create(name=text)
        return http.JsonResponse(
            {
                "id": supplier.id,
                "text": supplier.name,
            }
        )

    def get_queryset(self):
        qs = Supplier.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
