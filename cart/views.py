from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from main.models import Book
from .models import Order, OrderItem, Payment
from django.conf import settings
import stripe
import random
import string

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))


@login_required
def add_to_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item, created = OrderItem.objects.get_or_create(book=book)
    order, created = Order.objects.get_or_create(
        user=request.user, is_ordered=False)
    order.items.add(order_item)
    order.save()
    messages.info(request, "Item successfully added to your cart.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def remove_from_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item = get_object_or_404(OrderItem, book=book)
    order = Order.objects.get(user=request.user, is_ordered=False)
    order.items.remove(order_item)
    order.save()
    messages.info(request, "Item successfully removed from your cart.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def order_view(request):
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        context = {
            'order': order_qs[0]
        }
        return render(request, "cart/order_summary.html", context)
    return Http404


@login_required
def checkout(request):
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
    else:
        return Http404
    if request.method == "POST":
        # complete order
        order.ref_code = create_ref_code()

        # create stripe charge
        token = request.POST.get('stripeToken')
        charge = stripe.Charge.create(
            amount=int(order.get_total() * 75.90),  # cents
            currency="inr",
            source=token,
            description="Charge for {}".format(request.user.username),
        )

        # create payment object link to the order
        payment = Payment()
        payment.order = order
        payment.stripe_charge_id = charge.id
        payment.total_amount = order.get_total()
        payment.save()

        # add book to the users available books
        books = [item.book for item in order.items.all()]
        for book in books:
            request.user.userlibrary.books.add(book)

        order.is_ordered = True
        order.save()

        # redirect to user profile

        messages.success(request, "Your order was successfully placed")

        return redirect('/account/profile/')

    context = {
        'order': order,
    }

    return render(request, "cart/checkout.html", context)
