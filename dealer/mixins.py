from functools import wraps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class DealerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for class-based views — ensures user is logged in AND is a dealer."""

    def test_func(self):
        return hasattr(self.request.user, 'dealerprofile') and self.request.user.dealerprofile.is_dealer

    def handle_no_permission(self):
        messages.error(self.request, "You must be a registered dealer to access this page.")
        return redirect('dealer_login')


def dealer_required(view_func):
    """Decorator for function-based views — ensures user is logged in AND is a dealer."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in as a dealer to continue.")
            return redirect('dealer_login')
        if not hasattr(request.user, 'dealerprofile') or not request.user.dealerprofile.is_dealer:
            messages.error(request, "You must be a registered dealer to access this page.")
            return redirect('dealer_login')
        return view_func(request, *args, **kwargs)
    return wrapper
