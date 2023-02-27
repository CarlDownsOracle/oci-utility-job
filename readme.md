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

#### OCI Compartment

OCI IAM is based on Compartments.  This example assumes that all relevant resources are 
provisioned in a single non-root level compartment.  

We'll refer to it as **compartment X**.

#### OKE Cluster

Create an OCI Container Engine (OKE) instance in **compartment X.**

#### Load Balancer

Deploy a [Kubernetes Service of type load balancer](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer.htm) with an HTTPS listener.  

#### OCI Dynamic Group

Create a dynamic group for any instance in **compartment X**  to authorize your OKE worker nodes to perform job actions. 

    All {instance.compartment.id = 'ocid1.compartment.oc1..'}

#### OCI Policies

Create a policy in **compartment X**, granting the following roles (permission groups) to your dynamic group as is
required for the Job.

    Allow dynamic-group <your-dynamic-group> to manage load-balancers in compartment <name of X>
    Allow dynamic-group <your-dynamic-group> to use virtual-network-family in compartment <name of X>



## Local Development

Obtain your OCI configuration file by:

- Downloading it from the OCI Console via the User Settings / Capabilities page. 
- Installing the [OCI CLI](https://enabling-cloud.github.io/oci-learning/manual/OciCliUpAndRunningOnWindows.html)

Your [OCI configuration](https://docs.oracle.com/en-us/iaas/tools/python/2.93.0/configuration.html) goes here:

    % cat ~/.oci/config
    
Here is an example:

    [Default]
    user=ocid1.user.oc1..
    fingerprint=...
    tenancy=ocid1.tenancy.oc1....
    region=us-phoenix-1 (etc)
    key_file=~/.oci/your-key.pem

    [Another]
    user=ocid1.user.oc1..
    fingerprint=...
    ...

You may have multiple profiles.  If so, set this environment 
variable to one of the named profiles.

    export OCI_CLI_PROFILE=Another

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

## Kubernetes Job

#### Build the Container and Push to OCIR

You need to be [logged into OCIR](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionslogintoocir.htm) before running this.

    source job-build-tag-push.sh

#### Configure the job.yaml file

This YAML runs the job with action = '**assure-lb-cipher-suite**'.  Update the YAML file with your compartment ID and target cipher suite beforehand.

    metadata:
      name: oci-utility-job-configmap
    data:
      job-action: "assure-lb-cipher-suite"
      job-arg1: "oci-compatible-ssl-cipher-suite-v1"
    #  job-arg-cipher-suite-name: "oci-modern-ssl-cipher-suite-v1"
    #  job-arg-cipher-suite-name: "oci-default-ssl-cipher-suite-v1"
      compartment-id: "<compartment OCID>"



#### Run the Job

If you have not done so, [configure an 'ocirsecret'](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengpullingimagesfromocir.htm) in order for OKE to pull your Docker image from OCIR.

    source job.run.sh

#### Review Job Results

Tail the logs that the job outputs.

    source job-tail-logs.sh

#### Successful Job Output:

Output shows **"updated":true** along with current (old) and newly assigned cipher suite for load balancer listeners that are modified.


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

# References

### [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/)

[Python API](https://docs.oracle.com/en-us/iaas/tools/python/latest)

