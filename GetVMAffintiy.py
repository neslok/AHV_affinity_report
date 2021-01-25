#################################################################################################
# VM Affinity report
#
# By: Keith Olsen - keith.olsen@nutanix.com
#
# This script will query a cluster and create a csv report with VM's that have affinity configured.
#
# LIMITATIONS:
#   - It can only do one cluster at a time
#   - It only provides a single host that the VM is affinitiezed to. The VM may have an affinity for more
#       than what is identified in via this script.
#   - It will overwrite the csv file on each run - save your output file as required.
#
# Any questions or comments, please feel free to contact me.
#
# PLEASE NOTE - this script has not been audited for any security vulnerabilities.
#
# Please review and understand what it does, and how this may impact your environment.
#
# THIS CARRIES NO WARRANTY - EXPRESSED NOR IMPLIED AND IS FOR USE STRICTLY AT YOUR OWN RISK.
#
####################################################################################################

import requests
import json
from http.client import HTTPSConnection
from base64 import b64encode
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#
# Defines Prism Element variables

#peUserID = 'admin'
#pePassword = 'nutanix/4u'
#ClusterIP = '192.168.1.30'
ClusterIP = input("Enter cluster IP: ")
peUserID = input("Enter cluster login: ")
pePassword = input("Enter password: ")

# This sets up the https connection

c = HTTPSConnection(ClusterIP)

# # Creates encoded Authorization value

userpass = peUserID + ":" + pePassword
buserAndPass = b64encode(userpass.encode("ascii"))
authKey = (buserAndPass.decode("ascii"))

headers = {
    'Content-Type': "application/json",
    'Authorization': "Basic " + authKey,
    'cache-control': "no-cache"
}

# # Defines base url for API calls

baseurl = "https://" + ClusterIP + ":9440/PrismGateway/services/rest/v2.0/"

# Get list of all VMs on cluster

print("Getting list of VMs on cluster")

payload = {}

json_VMlist = requests.request("GET", baseurl + "vms", headers=headers, data=payload, verify=False).json()

VMlist = json.dumps(json_VMlist)

#print(VMlist)

# Get hosts info for cluster

print("Getting list of hosts in cluster")

payload = {}


json_HSTlist = requests.request("GET", baseurl + "hosts", headers=headers, data=payload, verify=False).json()

HSTlist = json.dumps(json_HSTlist)

#Create csv file called VmAffinity.csv in the same directory as where the script is executed

with open(ClusterIP + '_VmAffinity.csv', mode='w') as afinvm_file:
    afinvm_writer = csv.writer(afinvm_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    afinvm_writer.writerow(['VM name', 'Host name', 'Host IP'])

#Parse list of VMs looking for affinity setting

    print("Filtering for VMs with affinity configured")

    for eachVM in json_VMlist['entities']:
        # if (eachVM['power_state']) == "on":
        affinity = "affinity" in eachVM
        if affinity == True:
            HSTuuid = (eachVM['affinity']['host_uuids'][0])
            VMname = (eachVM['name'])

            #Collect host information for VM found with affinity set

            for eachHST in json_HSTlist['entities']:
                if HSTuuid == eachHST['uuid']:
                    HSTname = (eachHST['name'])
                    HSTip = (eachHST['hypervisor_address'])

            #Print Vms with affinity and to which host.

            print(VMname + " " + HSTname + " " + HSTip)

            #Write VM name, host name and host IP to file specified above

            afinvm_writer.writerow([VMname, HSTname, HSTip])