import json

import oci
from oci.config import from_file
from oci.identity import IdentityClient
from oci.load_balancer import LoadBalancerClient
import logging
import os

# ----------------------------------
# Environment
# ----------------------------------

dev_mode = os.getenv('dev_mode', 'False') == 'True'
profile_name = os.getenv('OCI_CLI_PROFILE', "not-configured")
compartment_id = os.getenv('compartment_id', "not-configured")

job_action = os.getenv('job_action', 'not-configured')
job_arg1 = os.getenv('job_arg1', "not-configured")


# ----------------------------------
# Job:
#   assure-lb-cipher-suite
# Arguments:
#   job-arg-cipher-suite-name
#       oci-modern-ssl-cipher-suite-v1
#       oci-compatible-ssl-cipher-suite-v1
#       oci-default-ssl-cipher-suite-v1
# ----------------------------------

cipher_suite_job_name = 'assure-lb-cipher-suite'

# ----------------------------------
# Client Setup
# ----------------------------------

identity_client = None
load_balancer_client = None

if dev_mode:
    config = from_file(profile_name=profile_name)
    identity_client = IdentityClient(config=config)
    load_balancer_client = LoadBalancerClient(config=config)
else:
    # OKE supports Instance Principals (not Resource Principals)
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    identity_client = IdentityClient(config={}, signer=signer)
    load_balancer_client = LoadBalancerClient(config={}, signer=signer)

# ----------------------------------
# Helper Methods
# ----------------------------------


def get_load_balancers():
    try:
        response = load_balancer_client.list_load_balancers(compartment_id=compartment_id)
        return response.data
    except Exception as e:
        logging.error({"exception": e})


def update_cipher_suite_for_all_load_balancers(target_suite_name):
    """
    """
    work = []

    try:
        response = load_balancer_client.list_load_balancers(compartment_id=compartment_id)
        load_balancers = response.data
        for load_balancer in load_balancers:
            work += update_cipher_suite_for_load_balancer(load_balancer.id, target_suite_name)

    except Exception as e:
        logging.error(e)

    return work


def update_cipher_suite_for_load_balancer(load_balancer_id, target_suite_name):
    """
    """
    work = []

    try:

        response = load_balancer_client.get_load_balancer(load_balancer_id)
        load_balancer = response.data

        for listener_name, listener in load_balancer.listeners.items():
            ssl_config = listener.ssl_configuration

            activity = dict()
            work.append(activity)
            activity['load_balancer_id'] = load_balancer_id
            activity['listener_name'] = listener_name

            if ssl_config:
                cipher_suite_name = ssl_config.cipher_suite_name
                activity['current_cipher_suite_name'] = cipher_suite_name

                if cipher_suite_name != target_suite_name:
                    update_listener_cipher_suite(load_balancer_id=load_balancer_id,
                                                 listener_name=listener_name,
                                                 cipher_suite_name=target_suite_name,
                                                 listener=listener,
                                                 ssl_config=ssl_config)

                    activity['new_cipher_suite_name'] = target_suite_name
                    activity['updated'] = True

    except Exception as e:
        logging.error(e)

    return work


def update_listener_cipher_suite(load_balancer_id, listener_name, cipher_suite_name, listener, ssl_config):
    """
    """
    ssl_configuration = oci.load_balancer.models.SSLConfigurationDetails()
    ssl_configuration.cipher_suite_name = cipher_suite_name
    ssl_configuration.certificate_name = ssl_config.certificate_name
    ssl_configuration.certificate_ids = ssl_config.certificate_ids

    details = oci.load_balancer.models.UpdateListenerDetails(ssl_configuration=ssl_configuration,
                                                             default_backend_set_name=listener_name,
                                                             protocol=listener.protocol,
                                                             port=listener.port)

    load_balancer_client.update_listener(update_listener_details=details,
                                         load_balancer_id=load_balancer_id,
                                         listener_name=listener_name)


def set_logging_level():
    logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
    loggers = [logging.getLogger()] + [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    [logger.setLevel(logging.getLevelName(logging_level)) for logger in loggers]


# ----------------------------------
# Main
# ----------------------------------


if __name__ == "__main__":

    set_logging_level()
    logging.info('oci_utility_job')
    logging.info('dev_mode = {}'.format(dev_mode))
    logging.info('compartment_id = {}'.format(compartment_id))
    logging.info('job_action = {}'.format(job_action))
    logging.info('job_arg1 = {}'.format(job_arg1))

    results = dict()

    if job_action == cipher_suite_job_name:
        results[job_action] = update_cipher_suite_for_all_load_balancers(job_arg1)
    else:
        logging.error('job_action not supported: {}'.format(job_action))

    logging.info(json.dumps(results, indent=4))

