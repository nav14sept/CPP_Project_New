from django.shortcuts import render
from cart.models import Order

# Create your views here.


def profile_view(request):
    order = Order.objects.filter(user=request.user, is_ordered=True)
    context = {
        'orders': order
    }
    return render(request, "account/profile.html", context)
