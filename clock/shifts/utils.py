# -*- coding: utf-8 -*-
from datetime import datetime

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

            try:
                return_kwargs = {
                    'year': request.session['last_kwargs']['year'],
                    'month': request.session['last_kwargs']['month'],
                }
            except KeyError:
                return_kwargs = {'year': datetime.now().strftime("%Y"), 'month': datetime.now().strftime("%m")}

            try:
                return_kwargs['contract'] = request.session['last_kwargs']['contract']
            except KeyError:
                return_kwargs['contract'] = '00'

            return reverse_lazy(last_view, kwargs=return_kwargs)
    return reverse_lazy(default_success)


def set_correct_session(request, k):
    try:
        return request.session['last_kwargs'][k]
    except KeyError:
        value = None
        if k == 'contract':
            value = '00'
        elif k == 'year':
            value = datetime.now().strftime("%Y")
        elif k == 'month':
            value = datetime.now().strftime("%m")
        return value


def get_current_shift(user):
    try:
        return Shift.objects.get(employee=user, shift_finished__isnull=True)
    except Shift.DoesNotExist:
        return None


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
    try:
        finished_shifts = Shift.objects.filter(employee=user).latest('shift_started')
    except Shift.DoesNotExist:
        # If the user just registered and does not have any shifts!
        return None

    # If the user has shifts
    if finished_shifts:
        # Are there any shifts finished for a non-default contract?
        if finished_shifts.contract is not None:
            # Return the contract of the latest shift

            return finished_shifts.contract.department

    # Return NoneObject for the default None-contract
    return None


def get_last_shifts(user, count=5):
    finished_shifts = Shift.objects.filter(employee=user, shift_finished__isnull=False)[:count]

    if not finished_shifts:
        return None

    return finished_shifts


def get_all_shifts(user):
    shifts = Shift.objects.filter(employee=user, shift_finished__isnull=False)

    months_with_shifts = []

    for shift in shifts:
        year = shift.shift_started.year
        month = shift.shift_started.month
        shift_dict = {'year': year, 'month': month}

        if shift_dict not in months_with_shifts:
            months_with_shifts.append(shift_dict)

    return months_with_shifts
