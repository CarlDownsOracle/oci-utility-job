# OCI Utility Job

This code sample demonstrates how to build and deploy a utility Kubernetes job to OCI Container Engine (OKE).


Here are the actions currently implemented:

| Action                 |                               Description                               | Notes                          |
|------------------------|:-----------------------------------------------------------------------:|:-------------------------------|
| assure-lb-cipher-suite | Assures all load balancer listener cipher suites match the target suite | Applies only to SSL listeners within your compartment |



## Getting Started

#### OCI Tenancy

You will need an OCI tenancy.  Check out the [OCI Cloud Free Tier](https://www.oracle.com/cloud/free/)!

See the [instructions](https://docs.oracle.com/en-us/iaas/tools/python/latest) for setting up API access to your tenancy.

This is a good article describing key [OCI concepts](https://blogs.oracle.com/developers/post/introduction-to-the-key-concepts-of-oracle-cloud-infrastructure).

#### OKE Cluster

You will need an OCI Container Engine (OKE) instance.

This example assumes that you have deployed a Service which provisions a load balancer with a listener that
supports https protocol.

#### OCI Dynamic Group

Create a dynamic group for any instance in a **named compartment**.
This authorizes your OKE worker nodes to perform job actions. 

    All {instance.compartment.id = 'ocid1.compartment.oc1..'}

#### OCI Policy for 'assure-lb-cipher-suite' Job

Create a policy in the same **named compartment**, granting the following
the permissions required for the 'assure-lb-cipher-suite' action.

    Allow dynamic-group <your-dynamic-group> to manage load-balancers in compartment <name>
    Allow dynamic-group <your-dynamic-group> to use virtual-network-family in compartment <name>



## Local Development Mode

Install the [OCI CLI](https://enabling-cloud.github.io/oci-learning/manual/OciCliUpAndRunningOnWindows.html) and configure it to have access to your tenancy.

View your [OCI configuration](https://docs.oracle.com/en-us/iaas/tools/python/2.93.0/configuration.html) (assuming Linux or Mac)

    % cat ~/.oci/config
    
Here is an example file config entry:

    [Default]
    user=ocid1.user.oc1..
    fingerprint=...
    tenancy=ocid1.tenancy.oc1....
    region=us-phoenix-1 (etc)
    key_file=~/.oci/your-key.pem

You may have multiple profiles other than 'Default'.  If so, et this environment 
variable to the ~/.oci/config profile.

    export OCI_CLI_PROFILE=Default

Set up a Python virtual env, activate it, and install the requirements in your virtual env:

    my-machine $ python3 -m venv venv
    my-machine $ source venv/bin/activate
    (venv) my-machine $ pip install -r requirements.txt

Export env variables expected by the script:

    export dev_mode="True"
    export compartment_id=<your compartment OCID>
    export job_action="assure-lb-cipher-suite"
    export job_arg1=<cipher suite name>

With that in place, export the env variables the Python script is expecting and run the main.py normally:

    python3 main.py

Successful output:

    INFO:root:oci_utility_job
    INFO:root:dev_mode = False
    INFO:root:compartment_id = <OCID>
    INFO:root:job_action = assure-lb-cipher-suite
    INFO:root:job_arg1 = oci-compatible-ssl-cipher-suite-v1
    INFO:root:{
        "assure-lb-cipher-suite": [
            {
                "load_balancer_id": "<OCID>",
                "listener_name": "TCP-80"
            },
            {
                "load_balancer_id": "<OCID>",
                "listener_name": "TCP-443",
                "current_cipher_suite_name": "oci-modern-ssl-cipher-suite-v1",
                "new_cipher_suite_name": "oci-compatible-ssl-cipher-suite-v1",
                "updated": true
            }
        ]
    }


## Kubernetes Job Mode

#### Build the Container and Push to OCIR

You need to be [logged into OCIR](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionslogintoocir.htm) before running this.

    source job.build-tag-push.sh

#### Run the 'assure-lb-cipher-suite' Job

This YAML runs
the job with action = 'assure-lb-cipher-suite'.  You will
need to update the YAML file with your compartment ID and
target cipher suite beforehand.

    source job.assure-lb-cipher-suite.sh

#### Review Job Results

Tail the logs that the job outputs.

    source job.logs.sh

# References

### [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/)

[Python API](https://docs.oracle.com/en-us/iaas/tools/python/latest)

