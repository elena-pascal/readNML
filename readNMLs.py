import f90nml
import h5py
from collections import OrderedDict
from pathlib import Path

##############################################################
#         h5 tools adapted from silx.io                      #
##############################################################

def _name_contains_string_in_list(name, strlist):
    if strlist is None:
        return False
    for filter_str in strlist:
        if filter_str in name:
            return True
    return False

def get_h5py_class(obj):
    """Returns the h5py class from an object.

    If it is an h5py object or an h5py-like object, an h5py class is returned.
    If the object is not an h5py-like object, None is returned.

    :param obj: An object
    :return: An h5py object
    """
    if hasattr(obj, "h5py_class"):
        return obj.h5py_class
    elif isinstance(obj, (h5py.File, h5py.Group, h5py.Dataset)):
        return obj.__class__
    else:
        return None

def is_file(obj):
    """
    True is the object is an h5py.File-like object.

    :param obj: An object
    """
    class_ = get_h5py_class(obj)
    if class_ is None:
        return False
    return issubclass(class_, h5py.File)

def is_group(obj):
    """
    True is the object is an h5py.Group-like object.

    :param obj: An object
    """
    class_ = get_h5py_class(obj)
    if class_ is None:
        return False
    return issubclass(class_, h5py.Group)

def h5todict(h5file, path="/", exclude_names=None):
    """Read a HDF5 file and return a nested dictionary with all data.

    Parameters
    ----------
    h5file: file name
    path: str,
       name of HDF5 group to use as dictionary root level,
       to read only a sub-group in the file
    exclude_names: list[str],
       groups and datasets whose name contains a string in this list will be ignored

    Returns
    -------
    ddict : Nested dictionary
    """
    if not is_file(h5file):
        # make it a h5py file
        h5f = h5py.File(h5file, 'r')
    else:
        # already a h5py file
        h5f = h5file

    ddict = {}
    for key in h5f[path]:
        # skip datasets with no relevant parameters
        if _name_contains_string_in_list(key, exclude_names):
            continue
        if is_group(h5f[path + "/" + key]):

            ddict[key] = h5todict(h5f,
                                  path + "/" + key,
                                  exclude_names=exclude_names)
        else:
            # Convert HDF5 dataset to numpy array
            ddict[key] = h5f[path + "/" + key][...]

    if not is_file(h5file):
        # close file, if we opened it
        h5f.close()

    return ddict
################################################################


def flatten_dict(pyobj, keystring=''):
    '''
    Returns a generator looping through the dict
    '''
    if type(pyobj) == dict:
        keystring = keystring + '/' if keystring else keystring
        for k in pyobj:
            yield from flatten_dict(pyobj[k], keystring + str(k))
    else:
        yield keystring, pyobj



class params():
    """Create a parameters namelist object containing all input parameters.

       This is a subclass of namalist which is a type of orderder dict.

       Parameters
       ----------
       prog : {'EMMCOpenCL', 'EMEBSDmaster', 'EMEBSDDI', 'EMEBSDDIpreview', 'EMFitOrientation'}
           The name of the EMsoft function for which input params
           should be collected
       sourcedir : str, optional, pathlib.Path instance
            The folder where input nml files are stored.
            Default is EMsoftData folder defined in EMsoftinit
       MC_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the Monte Carlo parameters.
            By default it is sourcedir+'EMMCOpenCL.nml'
       BethePar_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the Bethe parameters.
            By default it is sourcedir+'BetheParameters.nml'
       MP_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the Master Pattern parameters.
            By default it is sourcedir+'EMEBSDmaster.nml'
       DI_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the Dictionary Indexing parameters.
            By default it is sourcedir+'EMEBSDDI.nml'
       EBSDDIPrev_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the EBSD Preview parameters.
            By default it is sourcedir+'EMEBSDPreview.nml'
       FitOr_nml : str, optional, file-like object or pathlib.Path intance
            The nml file containing the EBSD Fit Orientation parameters.
            By default it is sourcedir+'EMFitOrientation.nml'

       Attributes
       ----------
       name: str,
            Name of program called with these parameters.
       sourcedir : str
            Source dir for nml files
       nml_files : list
            List of nml files with input paramaters
       h5_files : list
            List of h5 files with input data
       json_files : list
            List of json files with input paramaters
    """

    # TODO: EMsoftData must come from somewhere
    def __init__(self, prog, sourcedir = 'EMsoftData',
                        MC_nml       = 'EMMCOpenCL.nml',
                        MC_h5        = 'MCout.h5',
                        BethePar_nml = 'BetheParameters.nml',
                        MP_nml       = 'EMEBSDmaster.nml',
                        MP_h5        = 'MPout.h5',
                        DI_nml       = 'EMEBSDDI.nml',
                        DI_h5        = 'DIout.h5',
                        EBSDPrev_nml = 'EMEBSDDIpreview.nml',
                        FitOr_nml    = 'EMFitOrientation.nml'):

        # assign all init parameters as attributes
        self.prog        = prog
        self.sourcedir   = Path(sourcedir)

        # establish the nml, h5 and json files required
        # if (prog == 'EMMCOpenCL'):
        #     self.nml_files = kwargs.get(MC_nml)
        #
        # elif(prog == 'EMEBSDmaster'):
        #     self.nml_files = [kwargs.get(BethePar_nml), kwargs.get(MP_nml)]
        #     self.h5_files  = kwargs.get(MC_h5)

        if(prog == 'EMEBSDDI'):
            self.nml_file = self.sourcedir / DI_nml
            self.h5_file = self.sourcedir / MP_h5

        elif(prog == 'EMEBSDDIpreview'):
            self.nml_file = kwargs.get(EBSDPrev_nml)
            self.h5_file  = kwargs.get(DI_h5)

        elif(prog == 'EMFitOrientation'):
            self.nml_file = kwargs.get(FitOr_nml)
            self.h5_file  = kwargs.get(DI_h5)

        # dict with fortran types params
        self.par_dict = {'ipar': {}, 'fpar': {}, 'spar': {}}

        # read input into internal variables
        self.readInput()

        # initialise par variables
        self.initPar()

        # sort parameters in f90 order
        self.sortf90()


    def _loadNML(self):
        '''
        read all parameters in nml to a namelist parameter
        '''
        with open(self.nml_file) as file:
            nml_data = f90nml.read(file)

        self.nml_data = nml_data

    def _loadh5(self):
        '''
        read all parameters from the h5 file to a generator
        to prevent memory freeze for large datasets
        '''
        self.h5_data = flatten_dict(h5todict(self.h5_file,
                        exclude_names=['EMheader', 'NMLfiles']))


    def _sort_NML(self):
        '''
        Sort params from the nml_data in the order given by par_dict

        Uses
        ----------
        nml_data : namelist
            parameters in nml file
        par_dict : dict of OrderedDict
            {'ipar':OrderedDict, 'fpar':OrderedDict, 'spar':OrderedDict}
            of parameters required by fortran code

        Modifies
        --------
        par_dict : dict of OrderedDict
        '''
        nml_name = list(self.nml_data.keys())[0]
        for key, value in self.nml_data[nml_name].items():
            if key in self.par_dict['ipar']:
                self.par_dict['ipar'][key] = int(value)
            elif key in self.par_dict['fpar']:
                self.par_dict['fpar'][key] = float(value)
            elif key in self.par_dict['spar']:
                self.par_dict['spar'][key] = str(value)

    def _sort_h5(self):
        '''
        Sort params from h5_data in the order given by par_Dict

        Uses
        ----------
        h5gen : generator
            yield one parameters in h5 file at a time
        par_dict : dict of OrderedDict
            {'ipar':OrderedDict, 'fpar':OrderedDict, 'spar':OrderedDict}
            of parameters required by fortran code

        Modifies
        -------
        par_dict : dict of OrderedDict
        '''

        for key, value in self.h5_data:
            # strip the leading path to parameter key by reading
            # only the string after last '/' occurence
            key = key[key.rfind('/')+1:]

            if key in self.par_dict['ipar']:
                self.par_dict['ipar'][key] = int(value)
            elif key in self.par_dict['fpar']:
                self.par_dict['fpar'][key] = float(value)
            elif key in self.par_dict['spar']:
                self.par_dict['spar'][key] = str(value)


    def _initipar(self):
        """
        Initialise ipar as ordered dict.
        The order of parameters is predefined to match the fortran code.

        Parameters
        ---------
        prog : str, ['DI', 'refine']
            name of program for which parameters are needed
        """
        # variables starting with _ are computed from other parameters
        # variables starting with ! must be converted to int using specific rules

        # initialise ipar values
        self.par_dict['ipar'] = OrderedDict([("nx",                0), #1
                            ("globalworkgrpsz",   0), #2
                            ("num_el",            0), #3
                            ("totnum_el",         0), #4
                            ("multiplier",        0), #5
                            ("devid",             0), #6
                            ("platid",            0), #7
                            ("CrystalSystem",     0), #8
                            ("Natomtypes",        0), #9
                            ("SpaceGroupNumber",  0), #10
                            ("SpaceGroupSetting", 0), #11
                            ("numEbins",          0), #12
                            ("numzbins",          0), #13
                            ("!mcmode",           0), #14
                            ("numangles",         0), #15
                            ("nxten",             0), #16
                            ("npx",               0), #17
                            ("nthreads",          0), #18
                            ("numx",              0), #19
                            ("numy",              0), #20
                            ("num_or_in_qset",    0), #21
                            ("bin_factor",        0), #22
                            ("binx",              0), #23
                            ("biny",              0), #24
                            ("anglemode",         0), #25
                            ("ipf_wd",            0), #26
                            ("ipf_ht",            0), #27
                            ("nregions",          0), #28
                            ("!maskpattern",      0), #29
                            ("useROI",            0), #30
                            ("ROI1",              0), #31
                            ("ROI2",              0), #32
                            ("ROI3",              0), #33
                            ("ROI4",              0), #34
                            ("!inputtype",        0), #35
                            ("!uniform",          0), #36
                            ("numexpsingle",      0), #37
                            ("numdictsingle",     0), #38
                            ("nnk",               0), #39
                            ("_totnumexp",        0), #40
                            ("_noidea1",          0), #41
                            ("_noidea2",          0), #42
                            ("neulers",           0), #43
                            ("nvariants",         0), #44
                            ("nregionsmin",       0), #45
                            ("nregionsstepsize",  0), #46
                            ("numav",             0), #47
                            ("patx",              0), #48
                            ("paty",              0), #49
                            ("numw",              0), #50
                            ("numr",              0)  #51
                          ])


    def _initfpar(self):
        """
        Initialise fpar as ordered dict.
        The order of parameters is predefined to match the fortran code.

        Parameters
        ---------
        prog : str, ['DI', 'refine']
            name of program for which parameters are needed
        """
        # default values
        self.par_dict['fpar'] = OrderedDict([("sig",              .0), #1
                  ("omega",            .0), #2
                  ("EkeV",             .0), #3
                  ("Ehistmin",         .0), #4
                  ("Ebinsize",         .0), #5
                  ("depthmax",         .0), #6
                  ("depthstep",        .0), #7
                  ("sigstart",         .0), #8
                  ("sigend",           .0), #9
                  ("sigstep",          .0), #10
                  ("dmin",             .0), #11
                  ("c1",               .0), #12
                  ("c2",               .0), #13
                  ("c3",               .0), #14
                  ("xpc",              .0), #15
                  ("ypc",              .0), #16
                  ("delta",            .0), #17
                  ("thetac",           .0), #18
                  ("L",                .0), #19
                  ("beamcurrent",      .0), #20
                  ("dwelltime",        .0), #21
                  ("gamma",            .0), #22
                  ("maskradius",       .0), #23
                  ("highpassw",        .0), #24
                  ("step",             .0), #25
                  ("hipasswmax",       .0), #26
              ])


    def _initspar(self):
        """
        Initialise spar as ordered dict.
        The order of parameters is predefined to match the fortran code.

        Parameters
        ---------
        prog : str, ['DI', 'refine']
            name of program for which parameters are needed
        """

        # default values
        self.par_dict['spar'] = OrderedDict([('EMsoftpathname',       ''), #1
                            ('EMXtalFolderpathname', ''), #2
                            ('EMdatapathname',       ''), #3
                            ('EMtmppathname',        ''), #4
                            ('EMsoftLibraryLocation',''), #5
                            ('EMSlackWebHookURL',    ''), #6
                            ('EMSlackChannel',       ''), #7
                            ('UserName',             ''), #8
                            ('UserLocation',         ''), #9
                            ('UserEmail',            ''), #10
                            ('EMNotify',             ''), #11
                            ('Develop',              ''), #12
                            ('Release',              ''), #13
                            ('h5copypath',           ''), #14
                            ('EMsoftplatform',       ''), #15
                            ('EMsofttestpath',       ''), #16
                            ('EMsoftTestingPath',    ''), #17
                            ('EMsoftversion',        ''), #18
                            ('Configpath',           ''), #19
                            ('Templatepathname',     ''), #20
                            ('Resourcepathname',     ''), #21
                            ('Homepathname',         ''), #22
                            ('OpenCLpathname',       ''), #23
                            ('Templatecodefilename', ''), #24
                            ('WyckoffPositionsfilename',''), #25
                            ('Randomseedfilename',      ''), #26
                            ('EMsoftnativedelimiter',   ''), #27
        ])


    def initPar(self):
        self._initipar()
        self._initfpar()
        self._initspar()

    def readInput(self):
        self._loadNML()
        self._loadh5()

    def sortf90(self):
        self._sort_NML()
        self._sort_h5()

# class DIparams(params):
#     '''
#     Subclass of params for dictionary indexing
#     '''
#     def __init__(self, *args, **kwargs):
#         super(params, self).__init__(*args, **kwargs)
#         self.prog = 'EMEBSDDI'



foo = params('EMEBSDDI', sourcedir='testNMLs/', MP_h5='Ni-master-20kV.h5')
print('ipar values:', foo.par_dict['ipar'].values())
print()
print('all par in dict:', foo.par_dict)
print ()
print('par.nml_data', foo.nml_data)
