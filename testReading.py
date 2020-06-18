from readNMLs import readMC, readEBSDDI, readEBSDMaster, readBetheParams, readEBSDDIpreview

###################################################
################# test the things #################
###################################################

pathtoTestNMLs = 'testNMLs/'

################## BetheParams #####################
betheParamsfile = pathtoTestNMLs + 'BetheParameters.nml'
readBetheparams = readBetheParams(betheParamsfile)

# there should be 4 entries
assert len(readBetheparams)==4, \
        'dictionary %s has fewer elements than expected' % betheParamsfile


####################### MC ###########################
mcParamsfile = pathtoTestNMLs + 'EMMCOpenCL.nml'
readMCParams = readMC(mcParamsfile)

# there should be 24 entries
assert len(readMCParams)==24, \
        'dictionary %s has fewer elements than expected' % mcParamsfile


##################### masterEBSD ######################
masterEBSDfile = pathtoTestNMLs + 'EMEBSDmaster.nml'
readEBSDMasterParams = readEBSDMaster(masterEBSDfile)

# there should be 11 entries
assert len(readEBSDMasterParams)==11, \
        'dictionary %s has fewer elements than expected' % masterEBSDfile


######################### EBSDDI #######################
EBSDDIfile = pathtoTestNMLs + 'EMEBSDDI.nml'
readEBSDMDIParams = readEBSDDI(EBSDDIfile)

# there should be 46 entries
assert len(readEBSDMDIParams)==46, \
        'dictionary %s has fewer elements than expected' % EBSDDIfile


######################### EBSDDIpreview #######################
EBSDDIpreviewfile = pathtoTestNMLs + 'EMEBSDDIpreview.nml'
readEBSDDIpreviewParams = readEBSDDIpreview(EBSDDIpreviewfile)

# there should be 11 entries
assert len(readEBSDDIpreviewParams)==11, \
        'dictionary %s has fewer elements than expected' % EBSDDIpreviewfile
