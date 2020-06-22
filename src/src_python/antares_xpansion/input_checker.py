"""
    module to perform checks on antares xpansion input data
"""

import configparser
import sys
import os
import shutil

##########################################
# Checks related to profile/capacity files
##########################################

def check_profile_file(filename_path):
    """
        verifies if a given profile file is valid and indicates if it is a null profile or not

        :param filename_path: path to the profile file to check

        :return: returns False if the profile is null
    """
    #check file existence
    if not os.path.isfile(filename_path):
        print('Illegal value : option can be 0, 1 or an existent filename.\
                 %s is not an existent file' % filename_path)
        sys.exit(0)

    profile_column = []
    with open(filename_path, 'r') as profile_file:
        for idx, line in enumerate(profile_file):
            try:
                line_value = float(line.strip())
                profile_column.append(line_value)
            except ValueError:
                print('Line %d in file %s is not a single non-negative value'
                      % (idx+1, filename_path))
                sys.exit(0)
            if line_value < 0:
                print('Line %d in file %s indicates a negative value'
                      % (idx+1, filename_path))
                sys.exit(0)

    if len(profile_column) != 8760:
        print('file %s does not have 8760 lines'
              % filename_path)
        sys.exit(0)

    return any(profile_column)

##########################################
# Checks related to weights files
##########################################

def check_weights_file(filename_path):
    """
        checks that the yearly-weights file exists and has correct format:
            column of non-negative weights
            sum of weights is positive
        :return: True if the file has correct format, Exists otherwise
    """

    #check file existence
    if not os.path.isfile(filename_path):
        print('Illegal value : %s is not an existent yearly-weights file'
              % filename_path)
        sys.exit(0)

    null_weights = True
    with open(filename_path, 'r') as weights_file:
        for idx, line in enumerate(weights_file):
            try:
                line_value = float(line.strip())
                if line_value > 0:
                    null_weights = False
                elif line_value < 0:
                    print('Line %d in file %s indicates a negative value'
                          % (idx+1, filename_path))
                    sys.exit(0)
            except ValueError:
                print('Line %d in file %s is not a single non-negative value'
                      % (idx+1, filename_path))
                sys.exit(0)

    if null_weights:
        print('file %s : all values are null'
              % filename_path)
        sys.exit(0)

    return True


##########################################
# Checks related to candidates.ini
##########################################

def check_candidate_option_type(option, value):
    """
        verifies if a given option value has the correct type corresponding allowed for this option

        :param option: the treated option
        :param value: the value assigned to the option

        :return: True if the value has an appropriate type, False or exist otherwise
    """
    options_types = {'name' : 'string',
                     'enable' : 'string',
                     'candidate-type' : 'string',
                     'investment-type' : 'string',
                     'link' : 'string',
                     'annual-cost-per-mw' : 'non-negative',
                     'unit-size' : 'non-negative',
                     'max-units' : 'non-negative',
                     'max-investment' : 'non-negative',
                     'relaxed' : 'string',
                     'has-link-profile' : 'string',
                     'has-link-profile-indirect' : 'string',
                     'link-profile' : 'string',
                     'link-profile-indirect' : 'string',
                     'already-installed-capacity' : 'non-negative',
                     'already-installed-link-profile' : 'string',
                     'already-installed-link-profile-indirect' : 'string'}
    option_type = options_types.get(option)
    if option_type is None:
        print('check_candidate_option_type: %s option not recognized in candidates file.' % option)
        sys.exit(0)
    else:
        if option_type == 'string':
            return True
        elif option_type == 'numeric':
            return value.isnumeric()
        elif option_type == 'non-negative':
            try:
                return float(value) >= 0
            except ValueError:
                return False
        else:
            print('check_candidate_option_type: Non handled data type %s for option %s'
                  % (option_type, option))
            sys.exit(0)

def check_candidate_option_value(option, value):
    """
        verifies if a given option value belongs to the list of allowed values for that option

        :param option: the treated option
        :param value: the value to check

        :return: True if the value is legal or is not to be checked. Exists otherwise.
    """
    antares_links_list = None
    options_legal_values = {'name' : None,
                            'enable' : ["true", "false"],
                            'candidate-type' : ["investment", "decommissioning"],
                            'investment-type' : None,
                            'link' : antares_links_list,
                            'annual-cost-per-mw' : None,
                            'unit-size' : None,
                            'max-units' : None,
                            'max-investment' : None,
                            'relaxed' : ["true", "false"],
                            'has-link-profile' : ["true", "false"],
                            'has-link-profile-indirect' : ["true", "false"],
                            'link-profile' : None,
                            'link-profile-indirect' : None,
                            'already-installed-capacity' : None,
                            'already-installed-link-profile' : None,
                            'already-installed-link-profile-indirect' : None}
    legal_values = options_legal_values.get(option)
    if legal_values is None:
        return True
    elif value.lower() in legal_values:
        return True
    else:
        print('check_candidate_option_value: Illegal value %s for option %s allowed values are: %s'
              % (value, option, legal_values))
        sys.exit(0)

def check_candidate_name(name, section):
    """
        checks that the candidate's name is not empty and does not contain a space
    """
    if (not name) or (name == "NA"):
        print('Error candidates name cannot be empty : found in section %s' % section)
        sys.exit(0)
    if ' ' in name:
        print('Error candidates name should not contain space, found in section %s in "%s"'
              % (section, name))
        sys.exit(0)

def check_candidate_link(link, section):
    """
        checks that the candidate's link is not empty
    """
    if (not link) or (link == "NA"):
        print('Error candidates link cannot be empty : found in section %s' % section)
        sys.exit(0)

def check_candidates_file(driver):
    """
        checks that a candidate file related to an XpansionDriver has the correct format

        :param driver: the XpansionDriver pointing to the candidates file

        :return: Exists if the candidates files has the wrong format.
    """
    default_values = {'name' : 'NA',
                      'enable' : 'true',
                      'candidate-type' : 'investment',
                      'investment-type' : 'generation',
                      'link' : 'NA',
                      'annual-cost-per-mw' : '0',
                      'unit-size' : '0',
                      'max-units' : '0',
                      'max-investment' : '0',
                      'Relaxed' : 'false',
                      'has-link-profile' : 'false',
                      'has-link-profile-indirect' : 'false',
                      'link-profile' : '1',
                      'link-profile-indirect' : '1',
                      'already-installed-capacity' : '0',
                      'already-installed-link-profile' : '1',
                      'already-installed-link-profile-indirect' : '1'}
    ini_file = configparser.ConfigParser(default_values)
    ini_file.read(driver.candidates())

    config_changed = False

    #check attributes types and values
    for each_section in ini_file.sections():
        for (option, value) in ini_file.items(each_section):
            if not check_candidate_option_type(option, value):
                print("value %s for option %s has the wrong type!" % (value, option))
                sys.exit(0)
            check_candidate_option_value(option, value)

    # check that name is not empty and does not have space
    # check that link is not empty
    for each_section in ini_file.sections():
        check_candidate_name(ini_file[each_section]['name'].strip(), each_section)
        check_candidate_link(ini_file[each_section]['link'].strip(), each_section)

    # check some attributes unicity : name and links
    unique_attributes = ["name", "link"]
    for verified_attribute in unique_attributes:
        unique_values = set()
        for each_section in ini_file.sections():
            value = ini_file[each_section][verified_attribute].strip()
            if value in unique_values:
                print('Error candidates %ss have to be unique, duplicate %s %s in section %s'
                      % (verified_attribute, verified_attribute, value, each_section))
                sys.exit(0)
            else:
                unique_values.add(value)

    #check exclusion between max-investment and (max-units, unit-size) attributes
    for each_section in ini_file.sections():
        max_invest = float(ini_file[each_section]['max-investment'].strip())
        unit_size = float(ini_file[each_section]['unit-size'].strip())
        max_units = float(ini_file[each_section]['max-units'].strip())
        if max_invest != 0:
            if max_units != 0 or unit_size != 0:
                print("Illegal values in section %s: cannot assign non-null values simultaneously \
                      to max-investment and (unit-size or max_units)" % (each_section))
                sys.exit(0)
        elif max_units == 0 or unit_size == 0:
            print("Illegal values in section %s: need to assign non-null values to max-investment \
                  or (unit-size and max_units)" % (each_section))
            sys.exit(0)

    #check attributes profile is 0, 1 or an existent filename
    profile_attributes = ['link-profile', 'link-profile-indirect', 'already-installed-link-profile',
                          'already-installed-link-profile-indirect']
    for each_section in ini_file.sections():
        has_a_profile = False
        for attribute in profile_attributes:
            value = ini_file[each_section][attribute].strip()
            if value == '0':
                continue
            elif value == '1':
                has_a_profile = True
            else:
                has_a_profile = has_a_profile or check_profile_file(driver.capacity_file(value))
        if not has_a_profile:
            #remove candidate if it has no profile
            print("candidate %s will be removed!" % ini_file[each_section]["name"])
            ini_file.remove_section(each_section)
            config_changed = True

    #check coherence between has-link-profile and link-profile values
    linked_attributes = [["has-link-profile", "link-profile"],
                         ["has-link-profile-indirect", "link-profile-indirect"]]
    for each_section in ini_file.sections():
        for attributes in linked_attributes:
            has_link_value = ini_file[each_section][attributes[0]].strip()
            link_profile_value = ini_file[each_section][attributes[1]].strip()
            profile_exists = os.path.isfile(driver.capacity_file(link_profile_value))
            if (has_link_value == "true") and (not profile_exists):
                print('Incoherence in candidate %s: %s set to true while no %s file was specified'
                      % (ini_file[each_section]["name"].strip(),
                         attributes[0], attributes[1]))
                sys.exit(0)
            if (has_link_value == "false") and (profile_exists):
                print('Incoherence in candidate %s: %s set to false while a valid %s file was specified'
                      % (ini_file[each_section]["name"].strip(),
                         attributes[0], attributes[1]))
                sys.exit(0)

    if config_changed:
        shutil.copyfile(driver.candidates(), driver.candidates()+".bak")
        with open(driver.candidates(), 'w') as out_file:
            ini_file.write(out_file)
        print("%s file was overwritten! backup file %s created"
              % (driver.candidates(), driver.candidates()+".bak"))

##########################################
# Checks related to settings.ini
##########################################
def check_setting_option_type(option, value):
    """
        checks that a given option value has the correct type

        :param option: name of the option to verify from settings file
        :param value: value of the option to verify

        :return: True if the option has the correct type,
                 False or exists if the value has the wrong type
    """

    options_types = {'method' : 'string',
                     'uc_type' : 'string',
                     'master' : 'string',
                     'optimality_gap' : 'double',
                     'cut_type' : 'string',
                     'week_selection' : 'string',
                     'max_iteration' : 'integer',
                     'relaxed_optimality_gap' : 'string',
                     'solver' : 'string',
                     'timelimit' : 'integer',
                     'yearly_weights' : 'string'}
    option_type = options_types.get(option)
    if option_type is None:
        print('check_setting_option_type: Illegal %s option in candidates file.' % option)
        sys.exit(0)
    else:
        if option_type == 'string':
            return True
        elif option_type == 'numeric':
            return value.isnumeric()
        elif option_type == 'double':
            try:
                float(value)
                return True
            except ValueError:
                return False
        elif option_type == 'integer':
            if value in ["+Inf", "-Inf", "+infini", "-infini"]:
                return True
            try:
                int(value)
                return True
            except ValueError:
                return False
        else:
            print('check_setting_option_type: Non handled data type %s for option %s'
                  % (option_type, option))
            sys.exit(0)

def check_setting_option_value(option, value):
    """
        checks that an option has a legal value

        :param option: name of the option to verify from settings file
        :param value: value of the option to verify

        :return: True if the option has the correct type, exists if the value has the wrong type
    """

    options_legal_values = {'method' : ['benders_decomposition'],
                            'uc_type' : ['expansion_accurate', 'expansion_fast'],
                            'master' : ['relaxed', 'integer', 'full_integer'],
                            'optimality_gap' : None,
                            'cut_type' : ['average', 'yearly', 'weekly'],
                            'week_selection' : ['true', 'false'],
                            'max_iteration' : None,
                            'relaxed_optimality_gap' : None,
                            'solver' : ['Cplex', 'Xpress', 'Cbc', 'Sirius', 'Gurobi', 'GLPK'],
                            'timelimit' : None,
                            'yearly_weights' : None}
    legal_values = options_legal_values.get(option)

    if (legal_values is not None) and (value in legal_values):
        return True

    if option == 'optimality_gap':
        if (value == "-Inf") or (float(value) >= 0):
            return True
    elif option == 'max_iteration':
        if value in ["+Inf", "+infini"]:
            return True
        else:
            try:
                max_iter = int(value)
                if (max_iter == -1) or (max_iter > 0):
                    return True
            except ValueError:
                print('Illegal value %s for option %s : only -1 or positive values are allowed'
                      % (value, option))
                sys.exit(0)
    elif option == "relaxed_optimality_gap":
        if value.strip().endswith("%"):
            try:
                gap = float(value[:-1])
                if (gap >= 0) and (gap <= 100):
                    return True
            except ValueError:
                print('Illegal value %s for option %s: legal format "X%%" with X between 0 and 100'
                      % (value, option))
                sys.exit(0)
    elif option == 'timelimit':
        if (value in ["+Inf", "+infini"]):
            return True
        else:
            try:
                timelimit = int(value)
                if timelimit > 0:
                    return True
            except ValueError:
                print('Illegal value %s for option %s : only positive values are allowed'
                      % (value, option))
                sys.exit(0)

    print('check_candidate_option_value: Illegal value %s for option %s' % (value, option))
    sys.exit(0)
    return False

def check_settings_file(driver):
    """
        checks that a settings file related to an XpansionDriver has the correct format

        :param driver: the XpansionDriver pointing to the settings file

        :return: Exists if the candidates files has the wrong format.
    """
    with open(driver.settings(), 'r') as file_l:
        options = dict(
            {line.strip().split('=')[0].strip(): line.strip().split('=')[1].strip()
             for line in file_l.readlines()})

    #TODO stil unused : force these values if needed
    default_values = {'method' : 'benders_decomposition',
                      'uc_type' : 'expansion_fast',
                      'master' : 'integer',
                      'optimality_gap' : '0',
                      'cut_type' : 'yearly',
                      'week_selection' : 'false',
                      'max_iteration' : '+infini',
                      'relaxed_optimality_gap' : '0.01',
                      'solver' : 'Cbc',
                      'timelimit' : '+infini'}

    for (option, value) in options.items():
        if not check_setting_option_type(option, value):
            print("check_settings : value %s for option %s has the wrong type!" % (value, option))
            sys.exit(0)
        check_setting_option_value(option, value)

    if options.get('yearly_weights', "") != "":
        if options.get("cut_type") == "average":
            print("check_settings : yearly_weights option can not be used when cut_type option is average")
            sys.exit(0)
        check_weights_file(driver.weights_file(options.get('yearly_weights', "")))