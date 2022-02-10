import secrets
import string
import docker


class pColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Docker client
dockerClient = docker.from_env(base_url="/var/run/docker.sock")


def getPassword():
    try:
        return str(input("Enter a secure root password: "))
    except:
        return getPassword()


def generateSecurePassword():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(64))


# SWARM
print('Creating the Swarm network!')
try:
    dockerClient.swarm.init()
except:
    print(f"{pColors.FAIL}Can't create the Swarm! Aborting{pColors.ENDC}")
    quit()


# NETWORKS
print('Creating networks!')
networks = []
try:
    networks.append(dockerClient.networks.create(
        name="web", driver="overlay", attachable=True, check_duplicate=True))
    networks.append(dockerClient.networks.create(
        name="content", driver="overlay", attachable=True, check_duplicate=True))
    networks.append(dockerClient.networks.create(
        name="local", driver="overlay", attachable=True, check_duplicate=True))
except BaseException as ex:
    print(f"{pColors.FAIL}Can't create a network! Aborting{pColors.ENDC}")
    print(pColors.FAIL + ex + pColors.ENDC)
    try:
        # Delete created networks
        for n in networks:
            dockerClient.networks.get(n['id']).remove()
    except:
        pass
    quit()


# Containers

print('Creating containers!')
print('Creating Mysql container :')
print("You've to enter a root password, leave blank to generate a 64 characters password.")
print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")
mysql_pwd = getPassword()
if mysql_pwd == "":
    mysql_pwd = generateSecurePassword()
    print(f"Your root password is: {mysql_pwd}")

try:
    dockerClient.secrets.create(name="mysql-root", data=mysql_pwd)
except:
    print(f"{pColors.FAIL}Can't create a new secret... Aborting{pColors.ENDC}")
    quit()

print("Mysql container created !")
