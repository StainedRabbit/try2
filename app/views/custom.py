from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from app.models import Sale
from app.models import Remittance


@login_required
def home(request):
    my_strings = [
        "So many good things to come!",
        "You are beautiful.",
    ]
    context = {
        "my_strings": my_strings,
    }
    return render(request, "app/home.html", context)


def dashboard(request):
    pending_orders = Sale.objects.filter(status="P")
    remittance = Remittance.objects.get(is_active=True)
    context = {
        "pending_orders": pending_orders,
        "remittance": remittance,
    }
    return render(request, "app/dashboard.html", context)
