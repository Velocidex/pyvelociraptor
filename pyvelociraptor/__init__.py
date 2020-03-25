from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import getpass
import os
import yaml

def LoadConfigFile(config_file=None, password=None, backend=default_backend()):
    if config_file is None:
        config_file = os.environ.get("VELOCIRAPTOR_API_FILE")

    if config_file is None:
        config_file = os.path.join(os.environ.get("HOME"), ".pyvelociraptorrc")

    try:
        config = yaml.safe_load(open(config_file).read())
    except Exception as e:
        raise TypeError("Unable to parse config file from %s: %s" % (config_file, e))

    while "ENCRYPTED" in config["client_private_key"]:
        try:
            password = getpass.getpass("Password: ").encode()
            pem = config["client_private_key"].encode("utf8")

            key = load_pem_private_key(pem, password=password, backend=backend)
            config["client_private_key"]= key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ).decode("utf8")

            break

        except (TypeError, ValueError) as e:
            print("Error: %s" % e)
            continue

    return config
