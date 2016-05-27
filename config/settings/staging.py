# -*- coding: utf-8 -*-
'''
Staging Configurations

- Basically use the production config, but only include rosetta here.
'''

from .production import *  # noqa

INSTALLED_APPS += ("rosetta", )
