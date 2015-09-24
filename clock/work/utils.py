from clock.work.models import Shift


# class ActiveEntryError(Exception):
#     """A user should have no more than one active entry at a given time."""
#     pass


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
    return user.contract_set.all()


def get_default_contract(user):
    """
    Returns the default institute of the user.
        - If the user only has one defined, then use this.
        - If he has more than one defined, let us look into his
          finished shifts and use the most recent one.
        - Otherwise use the one with the smallest ID.
    """

    contracts = get_all_contracts(user)
    finished_shifts = Shift.objects.filter(employee=user,
                                           shift_finished__isnull=False)

    if finished_shifts:
        return finished_shifts[0].contract

    return contracts
