from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors

sdk = atmcd()  # Load the atmcd library
codes = atmcd_codes

ret = sdk.Initialize("")  # Initialize camera
print("Function Initialize returned {}".format(ret))

if atmcd_errors.Error_Codes.DRV_SUCCESS == ret:

    (ret, iSerialNumber) = sdk.GetCameraSerialNumber()
    print("Function GetCameraSerialNumber returned {} Serial No: {}".format(
        ret, iSerialNumber))

    # Configure the acquisition
    ret = sdk.CoolerON()
    print("Function CoolerON returned {}".format(ret))

    ret = sdk.SetAcquisitionMode(codes.Acquisition_Mode.SINGLE_SCAN)
    print("Function SetAcquisitionMode returned {} mode = Single Scan".format(ret))

    ret = sdk.SetReadMode(codes.Read_Mode.FULL_VERTICAL_BINNING)
    print("Function SetReadMode returned {} mode = FVB".format(ret))

    ret = sdk.SetTriggerMode(codes.Trigger_Mode.INTERNAL)
    print("Function SetTriggerMode returned {} mode = Internal".format(ret))

    (ret, xpixels, ypixels) = sdk.GetDetector()
    print("Function GetDetector returned {} xpixels = {} ypixels = {}".format(
        ret, xpixels, ypixels))

    ret = sdk.SetExposureTime(0.01)
    print("Function SetExposureTime returned {} time = 0.01s".format(ret))

    (ret, fminExposure, fAccumulate, fKinetic) = sdk.GetAcquisitionTimings()
    print("Function GetAcquisitionTimings returned {} exposure = {} accumulate = {} kinetic = {}".format(
        ret, fminExposure, fAccumulate, fKinetic))

    ret = sdk.PrepareAcquisition()
    print("Function PrepareAcquisition returned {}".format(ret))

    # Perform Acquisition
    ret = sdk.StartAcquisition()
    print("Function StartAcquisition returned {}".format(ret))

    ret = sdk.WaitForAcquisition()
    print("Function WaitForAcquisition returned {}".format(ret))

    imageSize = xpixels
    (ret, arr, validfirst, validlast) = sdk.GetImages16(1, 1, imageSize)
    print("Function GetImages16 returned {} first pixel = {} size = {}".format(
        ret, arr[0], imageSize))

    # Clean up
    ret = sdk.ShutDown()
    print("Function ShutDown returned {}".format(ret))

else:
    print("Cannot continue, could not initialise camera")
