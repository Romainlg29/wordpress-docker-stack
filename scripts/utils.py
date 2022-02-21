import secrets
import string
import os

from abort import abort


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


def getPassword():
    try:
        return str(input("Enter a secure password: "))
    except:
        return getPassword()


def generateSecurePassword():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(64))


def getResponse(text: string):
    try:
        return str(input(text))
    except:
        return getResponse()


def checkService(dockerClient, service_id):
    try:
        dockerClient.services.get(service_id=service_id)
        return True
    except:
        return False


def pullDockerImage(dockerClient, name, tag):
    try:
        if name and tag:
            print(f"Pulling {name}/{tag} ... (This can take few minutes.)")
            dockerClient.images.pull(name, tag)
        elif name and not tag:
            print(f"Pulling {name} ... (This can take few minutes.)")
            dockerClient.images.pull(name)
        else:
            raise Exception
        print(
            f'{pColors.OKGREEN}Successfully pulled {name} from Docker Hub!{pColors.ENDC}')
    except:
        print(f'Cannot pull {name}/{tag} from Docker Hub!')
        abort()


# Update our compose template file
# Replace every placeholder with the right value from the .env file
# If the .env isn't correct it'll abort
def updateComposeFile(inp, out, service, image, version):
    f = open(inp, "r+")
    o = open(out, "wt")

    for l in f:
        o.write(l.replace('{SERVICE}', service).replace(
            '{NAME}', image).replace('{TAG}', version))
    f.close()
    o.close()
