
################################################################################
# This script should be sourced instead of executed if you want to
#   run your tests from the command line.
# You can also specify the parameters in the constructor of the ipamServer
#   class.
################################################################################


################################################################################
# Parameters to connect to the phpIPAM service
################################################################################

# Before running this script, go to phpIPAM server as admin user
#  -In the Administration/API section, create a new App ID and App Code to allow
#     the access for scan agents. Several scan agents can use the same App ID and
#     App Code, or share the same.
#     - App permissions: Set it to 'Read/Write'.
#     - App security: set it to 'User Token' by now.
#  -In the Administration/Groups section, create a new group for scan agents.
#  -In the Administation/Sections section, create edit all sections ad add rw
#     permissions for the new group for scan agents.
#  -In the Administration/Users section, create one or more users for your scan agents.
#     Agents can use the same user or different users. Add users to the new group
#     for scan agents.
#     - User role: set it to normal user.
#     - Authentication method: set it to local.

echo "Setting environment for MYIPAMClient.py"
# Set this variables with the needed values to allow this agent to the phpIPAM server
#   Each scan agent can use different credentials or share the same.
export MYIPAM_URL="https://myphpipam.example.com"
export MYIPAM_APPID="myipamclient"
export MYIPAM_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export MYIPAM_USER="myipamuser"
# If you don't provide this variable, the connection function will ask for the
#   password interactively.
export MYIPAM_PASSWD="ppppppppppppppppppppp"
# SSL not tested yet (use NONE to connect without SSL)
#   If you want to use SSL, set the path to the CA certificate file in PEM format.
export MYIPAM_CACERT="NONE"

echo "MYIPAM_URL=$MYIPAM_URL"
echo "MYIPAM_USER=$MYIPAM_USER"
#echo "MYIPAM_CACERT=$MYIPAM_CACERT"

echo "Run your tests after setting the environment with previous variables"

# You can also add your test script after this line to set the environment and run from here.

