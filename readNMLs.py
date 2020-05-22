# read master NML files


def readBetheParams(betheNMLfile):
    '''
    read all parameters in BetheParameters.nml to a dict
    '''

    with open(betheNMLfile) as file:
        #split into lines
        rawdata = file.read().split('\n')

    data = {}

    for line in rawdata:
        if line.strip(): # ignore empty lines
            if not line.startswith(("!"," !", " &", " /")): # ignore comment lines
                # split line at =
                parameter = line.split("=")

                # trim whitespaces and commas
                label = parameter[0].strip(" ")
                param = parameter[1].strip(",' ")

                if (label in ['c1', 'c2', 'c3', 'sgdbdiff']):
                    # assign float to dictionary
                    data[label] = float(param)

    # is the dict empty?
    assert bool(data), \
        'dictionary data is empty after reading %s' % betheNMLfile

    return data


def readMC(mcNMLfile):
    '''
    read all parameters in master.nml to a dict
    '''

    with open(mcNMLfile) as file:
        #split into lines
        rawdata = file.read().split('\n')

    data = {}

    for line in rawdata:
        if line.strip(): # ignore empty lines
            if not line.startswith(("!"," !", " &", " /")): # ignore comment lines
                line = line.partition('!')[0] # ignore in line comments
                # split line at =
                parameter = line.split("=")

                # trim whitespaces and commas
                label = parameter[0].strip(" ")

                # replace the D in '15.D0' with 0
                param = parameter[1].replace("D", "0").strip(",' ")

                if (label in ['mode', 'xtalname', 'dataname', 'Notify']):
                    # assign strings to dictionary
                    data[label] = param

                elif (label in ['numsx', 'ivolx', 'ivoly', 'ivolz',\
                                  'num_el', 'platid', 'devid', 'globalworkgrpsz',\
                                  'totalnum_el', 'multiplier']):
                    # assign int to dictionary
                    data[label] = int(param)

                elif (label in ['sig', 'omega', 'sigstart', 'sigend', 'sigstep',\
                                   'ivolstepx', 'ivolstepy', 'ivolstepz'\
                                   'EkeV', 'Ehistmin', 'Ebinsize', 'depthmax', 'depthstep']):
                    # assign float to dictionary
                    data[label] = float(param)

    # is the dict empty?
    assert bool(data), \
        'dictionary data is empty after reading %s' % mcNMLfile

    return data



def readEBSDMaster(masterEBSDNMLfile):
    '''
    read all parameters in master.nml to a dict
    '''

    with open(masterEBSDNMLfile) as file:
        #split into lines
        rawdata = file.read().split('\n')

    data = {}

    for line in rawdata:
        if line.strip(): # ignore empty lines
            if not line.startswith(("!"," !", " &", " /")): # ignore comment lines
                # split line at =
                parameter = line.split("=")

                # trim whitespaces and commas
                label = parameter[0].strip(" ")
                param = parameter[1].strip(",' ")

                if (label in ['energyfile', 'BetheParametersFile', \
                                'Notify', 'copyfromenergyfile', 'h5copypath']):
                    # assign strings to dictionary
                    data[label] = param

                elif (label in ['npx', 'nthreads']):
                    # assign int to dictionary
                    data[label] = int(param)

                elif (label in ['dmin']):
                    # assign float to dictionary
                    data[label] = float(param)

                elif (label in ['restart', 'uniform', 'useEnergyWeighting']):
                    # set boolean parameter
                    data[label] = True if 'TRUE' in param else False

    # is the dict empty?
    assert bool(data), \
        'dictionary data is empty after reading %s' % masterEBSDNMLfile

    return data



def readEBSDDI(EMBSDDINMLfile):
    '''
    read all parameters in master.nml to a dict
    '''

    with open(EMBSDDINMLfile) as file:
        #split into lines
        rawdata = file.read().split('\n')

    data = {}

    for line in rawdata:
        if line.strip(): # ignore empty lines
            if not line.startswith(("!"," !", " &", " /")): # ignore comment lines
                # split line at =
                parameter = line.split("=")

                # strip empty spaces from label
                label = parameter[0].strip(" ")

                # deal with multi-string entries
                if label in ['ROI', 'multidevid']:
                    data[label] = [int(par) for par in parameter[1].strip(", ").split(" ")]

                elif label in 'HDFstrings':
                    data['HDFstrings'] = [par.strip("'") for par in parameter[1].strip(", ").split(" ")]

                else:
                    # trim whitespaces and commas
                    param = parameter[1].strip(",' ")

                    if (label in ['indexingmode', 'Notify', 'maskpattern',\
                                    'scalingmode', 'expfile', 'inputtype', 'tmpfile',\
                                    'keeptmpfile', 'ctfile', 'angfile', 'eulerfile',\
                                    'dictfile', 'masterfile', 'refinementNMLfile']):
                        # assign strings to dictionary
                        data[label] = param

                    elif (label in ['ipf_wd', 'ipf_ht', 'nnk', 'nosm', 'nism',\
                                        'maskradius', 'nregions', 'ncubochoric',\
                                        'numsx', 'numsy', 'binning', 'numdictsingle',\
                                        'numexptsingle', 'nthreads', 'platid', 'devid',\
                                        'usenumd']):
                        # assign int to dictionary
                        data[label] = int(param)

                    elif (label in ['stepX', 'stepY', 'isangle', 'higpassw', 'L',\
                                        'thetac', 'delta', 'xpc', 'ypc', 'omega',\
                                        'energymin', 'energymax', 'beamcurrent', 'dwelltime',\
                                        'gammavalue']):
                        # assign float to dictionary
                        data[label] = float(param)

    # is the dict empty?
    assert bool(data), \
        'dictionary data is empty after reading %s' % EMBSDDINMLfile

    return data
