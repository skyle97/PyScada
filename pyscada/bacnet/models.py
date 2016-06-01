# -*- coding: utf-8 -*-
from pyscada.models import Device
from pyscada.models import Variable
from pyscada.models import BackgroundTask

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


from time import time



#@receiver(post_save, sender=ModbusDevice)
#@receiver(post_save, sender=ModbusVariable)
def _reinit_daq_daemons(sender, **kwargs):
	"""
	update the daq daemon configuration wenn changes be applied in the models
	"""
	BackgroundTask.objects.filter(label='pyscada.daq.daemon',done=0,failed=0).update(message='reinit',restart_daemon=True,timestamp = time())
