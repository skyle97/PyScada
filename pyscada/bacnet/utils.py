#!/usr/bin/python
# -*- coding: utf-8 -*-

# pyscada imports
from pyscada import log

# bacpypes imports
from bacpypes.app import LocalDeviceObject, BIPSimpleApplication
from bacpypes.apdu import ReadPropertyMultipleACK, ReadAccessResult
from bacpypes.apdu import ReadAccessResultElement, ReadAccessResultElementChoice
from bacpypes.apdu import WhoIsRequest, Error
from bacpypes.pdu import Address, GlobalBroadcast
from bacpypes.object import PropertyError
from bacpypes.errors import ExecutionError
from bacpypes.basetypes import ErrorType
from bacpypes.primitivedata import Atomic, Real, Unsigned
from bacpypes.constructeddata import Array, Any

# django imports 

# other 

def ReadPropertyToAny(obj, propertyIdentifier, propertyArrayIndex=None):
    """
    Author: Joel Bender
    eMail: joel@carrickbender.com
    
    Read the specified property of the object, with the optional array index,
    and cast the result into an Any object."""

    # get the datatype
    datatype = obj.get_datatype(propertyIdentifier)
    if datatype is None:
        raise ExecutionError(errorClass='property', errorCode='datatypeNotSupported')

    # get the value
    value = obj.ReadProperty(propertyIdentifier, propertyArrayIndex)
    if value is None:
        raise ExecutionError(errorClass='property', errorCode='unknownProperty')

    # change atomic values into something encodeable
    if issubclass(datatype, Atomic):
        value = datatype(value)
    elif issubclass(datatype, Array) and (propertyArrayIndex is not None):
        if propertyArrayIndex == 0:
            value = Unsigned(value)
        elif issubclass(datatype.subtype, Atomic):
            value = datatype.subtype(value)
        elif not isinstance(value, datatype.subtype):
            raise TypeError("invalid result datatype, expecting %s and got %s" \
                % (datatype.subtype.__name__, type(value).__name__))
    elif not isinstance(value, datatype):
        raise TypeError("invalid result datatype, expecting %s and got %s" \
            % (datatype.__name__, type(value).__name__))

    # encode the value
    result = Any()
    result.cast_in(value)

    # return the object
    return result
    
def ReadPropertyToResultElement(obj, propertyIdentifier, propertyArrayIndex=None):
    """
    Author: Joel Bender
    eMail: joel@carrickbender.com
    
    Read the specified property of the object, with the optional array index,
    and cast the result into an Any object."""

    # save the result in the property value
    read_result = ReadAccessResultElementChoice()

    try:
        read_result.propertyValue = ReadPropertyToAny(obj, propertyIdentifier, propertyArrayIndex)
    except PropertyError as error:
        read_result.propertyAccessError = ErrorType(errorClass='property', errorCode='unknownProperty')
    except ExecutionError as error:
        read_result.propertyAccessError = ErrorType(errorClass=error.errorClass, errorCode=error.errorCode)

    # make an element for this value
    read_access_result_element = ReadAccessResultElement(
        propertyIdentifier=propertyIdentifier,
        propertyArrayIndex=propertyArrayIndex,
        readResult=read_result,
        )

    # fini
    return read_access_result_element
    
class PyScadaApplication(BIPSimpleApplication):
    def __init__(self, device, address,interval=60):
        BIPSimpleApplication.__init__(self, device, address)
    """
    overide some methodes just for logging
    """
    def request(self, apdu):
       log.debug("request %r"%apdu)
       #print "request %r"%apdu
       BIPSimpleApplication.request(self, apdu)
        
    def response(self, apdu):
        log.debug("response %r"%apdu)
        #print "request %r"%apdu
        BIPSimpleApplication.response(self, apdu)
    
    def indication(self, apdu):
        log.debug("indication %s", "do_" + apdu.__class__.__name__)
        #print "indication %s", "do_" + apdu.__class__.__name__
        BIPSimpleApplication.indication(self, apdu)
        
    
    """
    do_... function for handling pdu responces
    """
    def do_IAmRequest(self, apdu):
        """Respond to an I-Am request."""
        log.debug("do_IAmRequest %r"%apdu)
        log.debug('pduSource = ' + repr(apdu.pduSource))
        log.debug('iAmDeviceIdentifier = ' + str(apdu.iAmDeviceIdentifier))
        log.debug('maxAPDULengthAccepted = ' + str(apdu.maxAPDULengthAccepted))
        log.debug('segmentationSupported = ' + str(apdu.segmentationSupported))
        log.debug('vendorID = ' + str(apdu.vendorID) + '\n')
        
    
    def do_ReadPropertyMultipleRequest(self, apdu):
        """Respond to a ReadPropertyMultiple Request."""

        # response is a list of read access results (or an error)
        resp = None
        read_access_result_list = []

        # loop through the request
        for read_access_spec in apdu.listOfReadAccessSpecs:
            # get the object identifier
            objectIdentifier = read_access_spec.objectIdentifier

            # check for wildcard
            if (objectIdentifier == ('device', 4194303)):
                objectIdentifier = self.localDevice.objectIdentifier

            # get the object
            obj = self.get_object_id(objectIdentifier)

            # make sure it exists
            if not obj:
                resp = Error(errorClass='object', errorCode='unknownObject', context=apdu)
                break

            # build a list of result elements
            read_access_result_element_list = []

            # loop through the property references
            for prop_reference in read_access_spec.listOfPropertyReferences:
                # get the property identifier
                propertyIdentifier = prop_reference.propertyIdentifier

                # get the array index (optional)
                propertyArrayIndex = prop_reference.propertyArrayIndex

                # check for special property identifiers
                if propertyIdentifier in ('all', 'required', 'optional'):
                    for propId, prop in obj._properties.items():
                        if (propertyIdentifier == 'all'):
                            pass
                        elif (propertyIdentifier == 'required') and (prop.optional):
                            continue
                        elif (propertyIdentifier == 'optional') and (not prop.optional):
                            continue

                        # read the specific property
                        read_access_result_element = ReadPropertyToResultElement(obj, propId, propertyArrayIndex)

                        # check for undefined property
                        if read_access_result_element.readResult.propertyAccessError \
                            and read_access_result_element.readResult.propertyAccessError.errorCode == 'unknownProperty':
                            continue

                        # add it to the list
                        read_access_result_element_list.append(read_access_result_element)

                else:
                    # read the specific property
                    read_access_result_element = ReadPropertyToResultElement(obj, propertyIdentifier, propertyArrayIndex)

                    # add it to the list
                    read_access_result_element_list.append(read_access_result_element)

            # build a read access result
            read_access_result = ReadAccessResult(
                objectIdentifier=objectIdentifier,
                listOfResults=read_access_result_element_list
                )

            # add it to the list
            read_access_result_list.append(read_access_result)

        # this is a ReadPropertyMultiple ack
        if not resp:
            resp = ReadPropertyMultipleACK(context=apdu)
            resp.listOfReadAccessResults = read_access_result_list

        # return the result
        self.response(resp)
    
    def request_whois(self):
        """whois [ <addr>] [ <lolimit> <hilimit> ]"""
        
        try:
            # build a request
            request = WhoIsRequest()
            # if (len(args) == 1) or (len(args) == 3):
            #     request.pduDestination = Address(args[0])
            #     del args[0]
            # else:
            request.pduDestination = GlobalBroadcast()

            # if len(args) == 2:
            #     request.deviceInstanceRangeLowLimit = int(args[0])
            #     request.deviceInstanceRangeHighLimit = int(args[1])

            # give it to the application
            self.request(request)

        except Exception as err:
            pass # TODO log