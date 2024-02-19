from enum import IntEnum


class readmodes(IntEnum):
    AC_READMODE_FULLIMAGE = 1
    AC_READMODE_SUBIMAGE = 2
    AC_READMODE_SINGLETRACK = 4
    AC_READMODE_FVB = 8
    AC_READMODE_MULTITRACK = 16
    AC_READMODE_RANDOMTRACK = 32
    AC_READMODE_MULTITRACKSCAN = 64


class stepmodes(IntEnum):
    AT_STEPMODE_CONSTANT = 0
    AT_STEPMODE_EXPONENTIAL = 1
    AT_STEPMODE_LOGARITHMIC = 2
    AT_STEPMODE_LINEAR = 3
    AT_STEPMODE_OFF = 100


class gatemodes(IntEnum):
    AT_GATEMODE_FIRE_AND_GATE = 0
    AT_GATEMODE_FIRE_ONLY = 1
    AT_GATEMODE_GATE_ONLY = 2
    AT_GATEMODE_CW_ON = 3
    AT_GATEMODE_CW_OFF = 4
    AT_GATEMODE_DDG = 5


class triggermodes(IntEnum):
    AC_TRIGGERMODE_INTERNAL = 1
    AC_TRIGGERMODE_EXTERNAL = 2
    AC_TRIGGERMODE_EXTERNAL_FVB_EM = 4
    AC_TRIGGERMODE_CONTINUOUS = 8
    AC_TRIGGERMODE_EXTERNALSTART = 16
    AC_TRIGGERMODE_EXTERNALEXPOSURE = 32
    AC_TRIGGERMODE_INVERTED = 0x40
    AC_TRIGGERMODE_EXTERNAL_CHARGESHIFTING = 0x80
    AC_TRIGGERMODE_BULB = 32


class acquistionModes(IntEnum):
    AC_ACQMODE_SINGLE = 1
    AC_ACQMODE_VIDEO = 2
    AC_ACQMODE_ACCUMULATE = 4
    AC_ACQMODE_KINETIC = 8
    AC_ACQMODE_FRAMETRANSFER = 16
    AC_ACQMODE_FASTKINETICS = 32
    AC_ACQMODE_OVERLAP = 64
    AC_ACQMODE_TDI = 128


class cameratype(IntEnum):
    AC_CAMERATYPE_PDA = 0
    AC_CAMERATYPE_IXON = 1
    AC_CAMERATYPE_ICCD = 2
    AC_CAMERATYPE_EMCCD = 3
    AC_CAMERATYPE_CCD = 4
    AC_CAMERATYPE_ISTAR = 5
    AC_CAMERATYPE_VIDEO = 6
    AC_CAMERATYPE_IDUS = 7
    AC_CAMERATYPE_NEWTON = 8
    AC_CAMERATYPE_SURCAM = 9
    AC_CAMERATYPE_USBICCD = 10
    AC_CAMERATYPE_LUCA = 11
    AC_CAMERATYPE_RESERVED = 12
    AC_CAMERATYPE_IKON = 13
    AC_CAMERATYPE_INGAAS = 14
    AC_CAMERATYPE_IVAC = 15
    AC_CAMERATYPE_UNPROGRAMMED = 16
    AC_CAMERATYPE_CLARA = 17
    AC_CAMERATYPE_USBISTAR = 18
    AC_CAMERATYPE_SIMCAM = 19
    AC_CAMERATYPE_NEO = 20
    AC_CAMERATYPE_IXONULTRA = 21
    AC_CAMERATYPE_VOLMOS = 22
    AC_CAMERATYPE_IVAC_CCD = 23
    AC_CAMERATYPE_ASPEN = 24
    AC_CAMERATYPE_ASCENT = 25
    AC_CAMERATYPE_ALTA = 26
    AC_CAMERATYPE_ALTAF = 27
    AC_CAMERATYPE_IKONXL = 28
    AC_CAMERATYPE_RES1 = 29
    AC_CAMERATYPE_ISTAR_SCMOS = 30
    AC_CAMERATYPE_IKONLR = 31
    AC_PIXELMODE_8BIT = 1


class SetFunctions(IntEnum):
    AC_SETFUNCTION_VREADOUT = 0x01
    AC_SETFUNCTION_HREADOUT = 0x02
    AC_SETFUNCTION_TEMPERATURE = 0x04
    AC_SETFUNCTION_MCPGAIN = 0x08
    AC_SETFUNCTION_EMCCDGAIN = 0x10
    AC_SETFUNCTION_BASELINECLAMP = 0x20
    AC_SETFUNCTION_VSAMPLITUDE = 0x40
    AC_SETFUNCTION_HIGHCAPACITY = 0x80
    AC_SETFUNCTION_BASELINEOFFSET = 0x0100
    AC_SETFUNCTION_PREAMPGAIN = 0x0200
    AC_SETFUNCTION_CROPMODE = 0x0400
    AC_SETFUNCTION_DMAPARAMETERS = 0x0800
    AC_SETFUNCTION_HORIZONTALBIN = 0x1000
    AC_SETFUNCTION_MULTITRACKHRANGE = 0x2000
    AC_SETFUNCTION_RANDOMTRACKNOGAPS = 0x4000
    AC_SETFUNCTION_EMADVANCED = 0x8000
    AC_SETFUNCTION_GATEMODE = 0x010000
    AC_SETFUNCTION_DDGTIMES = 0x020000
    AC_SETFUNCTION_IOC = 0x040000
    AC_SETFUNCTION_INTELLIGATE = 0x080000
    AC_SETFUNCTION_INSERTION_DELAY = 0x100000
    AC_SETFUNCTION_GATESTEP = 0x200000
    AC_SETFUNCTION_GATEDELAYSTEP = 0x200000
    AC_SETFUNCTION_TRIGGERTERMINATION = 0x400000
    AC_SETFUNCTION_EXTENDEDNIR = 0x800000
    AC_SETFUNCTION_SPOOLTHREADCOUNT = 0x1000000
    AC_SETFUNCTION_REGISTERPACK = 0x2000000
    AC_SETFUNCTION_PRESCANS = 0x4000000
    AC_SETFUNCTION_GATEWIDTHSTEP = 0x8000000
    AC_SETFUNCTION_EXTENDED_CROP_MODE = 0x10000000
    AC_SETFUNCTION_SUPERKINETICS = 0x20000000
    AC_SETFUNCTION_TIMESCAN = 0x40000000
    AC_SETFUNCTION_CROPMODETYPE = 0x80000000
    AC_SETFUNCTION_GAIN = 8
    AC_SETFUNCTION_ICCDGAIN = 8


class GetFunctions(IntEnum):
    AC_GETFUNCTION_TEMPERATURE = 0x01
    AC_GETFUNCTION_TARGETTEMPERATURE = 0x02
    AC_GETFUNCTION_TEMPERATURERANGE = 0x04
    AC_GETFUNCTION_DETECTORSIZE = 0x08
    AC_GETFUNCTION_MCPGAIN = 0x10
    AC_GETFUNCTION_EMCCDGAIN = 0x20
    AC_GETFUNCTION_HVFLAG = 0x40
    AC_GETFUNCTION_GATEMODE = 0x80
    AC_GETFUNCTION_DDGTIMES = 0x0100
    AC_GETFUNCTION_IOC = 0x0200
    AC_GETFUNCTION_INTELLIGATE = 0x0400
    AC_GETFUNCTION_INSERTION_DELAY = 0x0800
    AC_GETFUNCTION_GATESTEP = 0x1000
    AC_GETFUNCTION_GATEDELAYSTEP = 0x1000
    AC_GETFUNCTION_PHOSPHORSTATUS = 0x2000
    AC_GETFUNCTION_MCPGAINTABLE = 0x4000
    AC_GETFUNCTION_BASELINECLAMP = 0x8000
    AC_GETFUNCTION_GATEWIDTHSTEP = 0x10000
    AC_GETFUNCTION_GAIN = 0x10
    AC_GETFUNCTION_ICCDGAIN = 0x10


class Features(IntEnum):
    AC_FEATURES_POLLING = 1
    AC_FEATURES_EVENTS = 2
    AC_FEATURES_SPOOLING = 4
    AC_FEATURES_SHUTTER = 8
    AC_FEATURES_SHUTTEREX = 16
    AC_FEATURES_EXTERNAL_I2C = 32
    AC_FEATURES_SATURATIONEVENT = 64
    AC_FEATURES_FANCONTROL = 128
    AC_FEATURES_MIDFANCONTROL = 256
    AC_FEATURES_TEMPERATUREDURINGACQUISITION = 512
    AC_FEATURES_KEEPCLEANCONTROL = 1024
    AC_FEATURES_DDGLITE = 0x0800
    AC_FEATURES_FTEXTERNALEXPOSURE = 0x1000
    AC_FEATURES_KINETICEXTERNALEXPOSURE = 0x2000
    AC_FEATURES_DACCONTROL = 0x4000
    AC_FEATURES_METADATA = 0x8000
    AC_FEATURES_IOCONTROL = 0x10000
    AC_FEATURES_PHOTONCOUNTING = 0x20000
    AC_FEATURES_COUNTCONVERT = 0x40000
    AC_FEATURES_DUALMODE = 0x80000
    AC_FEATURES_OPTACQUIRE = 0x100000
    AC_FEATURES_REALTIMESPURIOUSNOISEFILTER = 0x200000
    AC_FEATURES_POSTPROCESSSPURIOUSNOISEFILTER = 0x400000
    AC_FEATURES_DUALPREAMPGAIN = 0x800000
    AC_FEATURES_DEFECT_CORRECTION = 0x1000000
    AC_FEATURES_STARTOFEXPOSURE_EVENT = 0x2000000
    AC_FEATURES_ENDOFEXPOSURE_EVENT = 0x4000000
    AC_FEATURES_CAMERALINK = 0x8000000
    AC_FEATURES_FIFOFULL_EVENT = 0x10000000
    AC_FEATURES_SENSOR_PORT_CONFIGURATION = 0x20000000
    AC_FEATURES_SENSOR_COMPENSATION = 0x40000000
    AC_FEATURES_IRIG_SUPPORT = 0x80000000


class PixelModes(IntEnum):
    AC_PIXELMODE_14BIT = 2
    AC_PIXELMODE_16BIT = 4
    AC_PIXELMODE_32BIT = 8
    AC_PIXELMODE_MONO = 0x000000
    AC_PIXELMODE_RGB = 0x010000
    AC_PIXELMODE_CMY = 0x020000


class EmGainModes(IntEnum):
    AC_EMGAIN_8BIT = 1
    AC_EMGAIN_12BIT = 2
    AC_EMGAIN_LINEAR12 = 4
    AC_EMGAIN_REAL12 = 8


class Features2(IntEnum):
    AC_FEATURES2_ESD_EVENTS = 1
    AC_FEATURES2_DUAL_PORT_CONFIGURATION = 2


class CameraCapabilities(IntEnum):
    AT_NoOfVersionInfoIds = 2
    AT_VERSION_INFO_LEN = 80
    AT_CONTROLLER_CARD_MODEL_LEN = 80
    AT_DDGLite_ControlBit_GlobalEnable = 0x01
    AT_DDGLite_ControlBit_ChannelEnable = 0x01
    AT_DDGLite_ControlBit_FreeRun = 0x02
    AT_DDGLite_ControlBit_DisableOnFrame = 0x04
    AT_DDGLite_ControlBit_RestartOnFire = 0x08
    AT_DDGLite_ControlBit_Invert = 0x10
    AT_DDGLite_ControlBit_EnableOnFire = 0x20
    AT_DDG_POLARITY_POSITIVE = 0
    AT_DDG_POLARITY_NEGATIVE = 1
    AT_DDG_TERMINATION_50OHMS = 0
    AT_DDG_TERMINATION_HIGHZ = 1
