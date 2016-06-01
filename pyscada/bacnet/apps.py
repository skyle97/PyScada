# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaBACnetConfig(AppConfig):
    name = 'pyscada.bacnet'
    verbose_name = _("PyScada BACnet Device")
