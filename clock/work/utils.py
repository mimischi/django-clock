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
        - If the user has any finished shifts, then return the contract
          of the last finished shift.
        - If no shifts were finished yet, but the user has defined contracts,
          return the contract that was added first.
        - If no contracts are defined, then return the NoneObject as default
    """
    # Filter all shifts (finished or not) from the current user
    finished_shifts = Shift.objects.filter(employee=user)

    # If the user has shifts
    if finished_shifts:
        # Are there any shifts finished for a non-default contract?
        if finished_shifts[0].contract is not None:
            # Return the contract of the latest shift
            return finished_shifts[0].contract.department

    # Return NoneObject for the defaukt None-contract
    return None
