# -*- coding: utf-8 -*-

from pyscada import log
from pyscada.bacnet.utils import PyScadaApplication

from bacpypes.core import run
from bacpypes.app import LocalDeviceObject

import sys, os


def create_local_device():
    # make a device object
    object_name = 'testdevice'          # TODO read from settings.PYSCADA_BACNET['objectName']
    max_apdu_length_accepted = 1024     # TODO read from settings.PYSCADA_BACNET['maxApduLengthAccepted']
    segmentation_supported = 'segmentedBoth' # TODO read from settings.PYSCADA_BACNET['segmentationSupported']
    vendor_identifier = 999             # TODO read from settings.PYSCADA_BACNET['vendorIdentifier']
    object_identifier = 599              # TODO read from settings.PYSCADA_BACNET['objectIdentifier']
    #ip_address = '130.149.228.226/25'    # TODO read from settings.PYSCADA_BACNET['ipAddress']
    ip_address = '192.168.228.117/24'    # TODO read from settings.PYSCADA_BACNET['ipAddress']

    '''
    'maxApduLengthAccepted': 1024
        , 'segmentationSupported': 'segmentedBoth'
        , 'maxSegmentsAccepted': 16
        , 'apduSegmentTimeout': 20000
        , 'apduTimeout': 3000
        , 'numberOfApduRetries': 3
     '''  
    
    this_device = LocalDeviceObject(
        objectName=object_name,
        objectIdentifier=int(object_identifier),
        maxApduLengthAccepted=int(max_apdu_length_accepted),
        segmentationSupported=segmentation_supported,
        vendorIdentifier=int(vendor_identifier),
        vendorName="Hello",
        )

    
    this_application = PyScadaApplication(this_device, ip_address)
    
    services_supported = this_application.get_services_supported()
    
    
    this_device.protocolServicesSupported = services_supported.value
    this_application.request_whois()
    run()
    
    
    
    
    
    
    
    
    
    
    