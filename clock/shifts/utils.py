# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy

from clock.shifts.models import Shift


def get_return_url(request, default_success):
    """
    Checks whether the user should be returned to the default_success view or to a special one. Is mostly used for the
    shift list views, as they can get filtered by month/year and contract ID. After updating/adding one, the user should
    be redirected to either:
        1) The standard shift list view (if no filters were specified)
        2) The previous visited view (if he updated / created a shift in the same month / contract)
        3) A filtered view which corresponds to the date/contract of the updated/added shift
    """
    if "shift" in request.session['last_visited'] and request.session['last_kwargs']:
            last_view = request.session['current_view_name']
            try:
                last_view = request.session['last_view_name']
            except KeyError:
                pass

            last_view = "shift:archive_month_contract_numeric"

            return_kwargs = {
                'year': request.session['last_kwargs']['year'],
                'month': request.session['last_kwargs']['month'],
                'contract': '00',
            }

            try:
                return_kwargs['contract'] = request.session['last_kwargs']['contract']
            except KeyError:
                pass

            return reverse_lazy(last_view, kwargs=return_kwargs)
    return reverse_lazy(default_success)


def get_current_shift(user):
    entries = Shift.objects.filter(employee=user, shift_finished__isnull=True)

    if not entries.exists():
        return None
    # if entries.count() > 1:
    #     raise ActiveEntryError('Only one active entry is allowed.')
    return entries[0]


def get_all_contracts(user):
    """
    Returns all contracts an user has signed.
    """
    return user.contract_set.all().order_by('id')


def get_default_contract(user):
    """
    Returns the default institute of the user.
        - If the user has any finished shifts, then return the contract
          of the last finished shift.
        - If no shifts were finished yet, but the user has defined contracts,
          return the contract that was added first.
        - If no contracts are defined, then return the NoneObject as default
    """
    # Filter all shifts (finished or not) from the current user
    finished_shifts = Shift.objects.filter(employee=user).latest('shift_started')

    # If the user has shifts
    if finished_shifts:
        # Are there any shifts finished for a non-default contract?
        if finished_shifts.contract is not None:
            # Return the contract of the latest shift

            return finished_shifts.contract.department

    # Return NoneObject for the default None-contract
    return None
