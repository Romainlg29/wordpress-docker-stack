import os

import subprocess
from scripts.utils import pullDockerImage

from utils import pColors, getPassword, generateSecurePassword, checkService
from abort import abort


def create_mysql_container(dockerClient):

    def updateComposeFile():
        f = open(f"../stack/mysql/docker-compose.yml.template", "r+")
        o = open(f"../stack/mysql/docker-compose.yml", "wt")

        for l in f:
            o.write(l.replace('{SERVICE}', os.getenv('MYSQL_SERVICE_NAME')).replace(
                '{NAME}', os.getenv('MYSQL_IMAGE')).replace('{TAG}', os.getenv('MYSQL_VERSION')))
        f.close()
        o.close()

    print(f"{pColors.HEADER}Creating the {os.getenv('MYSQL_IMAGE')} container (1/4){pColors.ENDC}")
    print("You've to enter a root password, leave blank to generate a 64 characters password.")
    print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")
    mysql_pwd = getPassword()
    if mysql_pwd == "":
        mysql_pwd = generateSecurePassword()
        print(
            f"Your root password is:{pColors.OKCYAN} {mysql_pwd} {pColors.ENDC}, please keep it secret!")

    try:
        dockerClient.secrets.create(name="mysql-root", data=mysql_pwd)
        print("Secret created!")
    except:
        print(f"{pColors.FAIL}Can't create a new secret...{pColors.ENDC}")
        abort()

    pullDockerImage(dockerClient, os.getenv(
        'MYSQL_IMAGE'), os.getenv('MYSQL_VERSION'))

    try:
        updateComposeFile()
    except:
        print(f"{pColors.FAIL}Cannot create the docker-compose.{pColors.ENDC}")
        abort()

    print("Buiding the image!")
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/mysql/docker-compose.yml", "local"])
    if checkService(f"local_{os.getenv('MYSQL_SERVICE_NAME')}") == False:
        print(
            f"{pColors.FAIL}Cannot detect {os.getenv('MYSQL_SERVICE_NAME')} service! Aborting{pColors.ENDC}")
        abort()

    print(f"{pColors.OKGREEN}{os.getenv('MYSQL_SERVICE_NAME')} container created ! (1/4){pColors.ENDC}")
    return mysql_pwd
