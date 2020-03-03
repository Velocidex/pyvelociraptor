import os
import yaml

def LoadConfigFile(config_file=None):
    if config_file is None:
        config_file = os.environ.get("VELOCIRAPTOR_API_FILE")

    if config_file is None:
        config_file = os.path.join(os.environ.get("HOME"), ".pyvelociraptorrc")

    try:
        config = yaml.safe_load(open(config_file).read())
    except Exception as e:
        raise TypeError("Unable to parse config file from %s: %s" % (config_file, e))

    return config
