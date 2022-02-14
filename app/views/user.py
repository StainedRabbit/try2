from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from dal import autocomplete
from app.models import User
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _


class CustomerAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = User.objects.all()
        if self.q:
            qs = qs.filter(
                Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q)
            )
        return qs
