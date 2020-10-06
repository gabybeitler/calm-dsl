# THIS FILE IS AUTOMATICALLY GENERATED.
# Disclaimer: Please test this file before using in production.
"""
Generated blueprint DSL (.py)
"""

import json  # no_qa
import os  # no_qa

from calm.dsl.builtins import *  # no_qa


# Secret Variables
BP_CRED_LOCAL_PASSWORD = read_local_file("BP_CRED_LOCAL_PASSWORD")
BP_CRED_DOMAIN_CRED_PASSWORD = read_local_file("BP_CRED_DOMAIN_CRED_PASSWORD")

# Credentials
BP_CRED_LOCAL = basic_cred(
    "administrator",
    BP_CRED_LOCAL_PASSWORD,
    name="LOCAL",
    type="PASSWORD",
    default=True,
    editables={"username": True, "secret": True},
)
BP_CRED_DOMAIN_CRED = basic_cred(
    "administrator@contoso.com",
    BP_CRED_DOMAIN_CRED_PASSWORD,
    name="DOMAIN_CRED",
    type="PASSWORD",
    editables={"username": True, "secret": True},
)


class AD_DNS_DHCP_SERVICES(Service):

    pass


class ADDNSDHCP_SERVERcalm_randomResources(AhvVmResources):

    memory = 4
    vCPUs = 2
    cores_per_vCPU = 1
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromImageService(
            "WindowsServer2016-Base.qcow2", bootable=True
        )
    ]
    nics = [AhvVmNic.NormalNic.ingress("vlan.0", cluster="Goten-1")]

    guest_customization = AhvVmGC.Sysprep.PreparedScript.withoutDomain(
        filename=os.path.join(
            "specs", "ADDNSDHCP_SERVERcalm_random_sysprep_unattend_xml.xml"
        )
    )


class ADDNSDHCP_SERVERcalm_random(AhvVm):

    name = "AD-DNS-DHCP_SERVER@@{calm_random}@@"
    resources = ADDNSDHCP_SERVERcalm_randomResources


class AD_DNS_DHCP_SERVER(Substrate):

    os_type = "Windows"
    provider_type = "AHV_VM"
    provider_spec = ADDNSDHCP_SERVERcalm_random
    provider_spec_editables = read_spec(
        os.path.join("specs", "AD_DNS_DHCP_SERVER_create_spec_editables.yaml")
    )
    readiness_probe = readiness_probe(
        connection_type="POWERSHELL",
        disabled=False,
        retries="5",
        connection_port=5985,
        address="@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        delay_secs="180",
        credential=ref(BP_CRED_LOCAL),
        editables_list=[
            "connection_type",
            "delay_secs",
            "connection_port",
            "timeout_secs",
        ],
    )


class Active_Directory_Package(Package):

    services = [ref(AD_DNS_DHCP_SERVICES)]

    @action
    def __install__():

        CalmTask.Exec.powershell(
            name="Install AD",
            filename=os.path.join(
                "scripts",
                "Package_Active_Directory_Package_Action___install___Task_InstallAD.ps1",
            ),
            cred=ref(BP_CRED_LOCAL),
            target=ref(AD_DNS_DHCP_SERVICES),
        )
        CalmTask.Exec.escript(
            name="Wait for VM to Install AD",
            filename=os.path.join(
                "scripts",
                "Package_Active_Directory_Package_Action___install___Task_WaitforVMtoInstallAD.py",
            ),
            target=ref(AD_DNS_DHCP_SERVICES),
        )
        CalmTask.Exec.powershell(
            name="Open Firewall Ports",
            filename=os.path.join(
                "scripts",
                "Package_Active_Directory_Package_Action___install___Task_OpenFirewallPorts.ps1",
            ),
            cred=ref(BP_CRED_LOCAL),
            target=ref(AD_DNS_DHCP_SERVICES),
        )
        CalmTask.Exec.powershell(
            name="Install DHCP",
            filename=os.path.join(
                "scripts",
                "Package_Active_Directory_Package_Action___install___Task_InstallDHCP.ps1",
            ),
            cred=ref(BP_CRED_DOMAIN_CRED),
            target=ref(AD_DNS_DHCP_SERVICES),
        )


class AD_DNS_DHCP_SERVER_Deployment(Deployment):

    name = "AD_DNS_DHCP_SERVER_Deployment"
    min_replicas = "1"
    max_replicas = "1"
    default_replicas = "1"

    packages = [ref(Active_Directory_Package)]
    substrate = ref(AD_DNS_DHCP_SERVER)


class Nutanix(Profile):

    deployments = [AD_DNS_DHCP_SERVER_Deployment]

    DOMAIN = CalmVariable.Simple(
        "contoso.com",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=True,
        description="Ex:- google.com",
    )

    DOMAIN_TYPE = CalmVariable.Simple(
        "DC",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=True,
        description="DC,ADC,CDC or RODC",
    )

    CHILD_DOMAIN = CalmVariable.Simple(
        "",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=True,
        description="Example:- yahoo.com is your main domain then your sub domain will be mail.yahoo.com.",
    )

    VMNAME = CalmVariable.Simple(
        "AD_DNS_DHCP",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=True,
        description="Hostname name/ VM name of the server",
    )


class ADDNSDHCP(Blueprint):

    services = [AD_DNS_DHCP_SERVICES]
    packages = [Active_Directory_Package]
    substrates = [AD_DNS_DHCP_SERVER]
    profiles = [Nutanix]
    credentials = [BP_CRED_LOCAL, BP_CRED_DOMAIN_CRED]
