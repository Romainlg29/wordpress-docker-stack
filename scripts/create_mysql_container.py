import os

import subprocess

from utils import pColors, getPassword, generateSecurePassword, checkService, pullDockerImage, updateComposeFile
from abort import abort


def create_mysql_container(dockerClient):

    print(f"{pColors.HEADER}Creating the {os.getenv('MYSQL_IMAGE')} container (1/4){pColors.ENDC}")
    print("You've to enter a root password, leave blank to generate a 64 characters password.")
    print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")

    # Ask for a password
    # If empty, it'll generate a secure one and return it to the user
    # It must be saved!
    mysql_pwd = getPassword()
    if mysql_pwd == "":
        mysql_pwd = generateSecurePassword()
        print(
            f"Your root password is:{pColors.OKCYAN} {mysql_pwd} {pColors.ENDC}, please keep it secret!")

    # Create a docker secret to store the MYSQL root password
    # It'll be saved as mysql-root
    try:
        dockerClient.secrets.create(name="mysql-root", data=mysql_pwd)
        print("Secret created!")
    except:
        print(f"{pColors.FAIL}Can't create a new secret...{pColors.ENDC}")
        abort()

    # Here' we're pulling the needed image from Docker Hub
    # Image name comes from the .env file
    # It must be filled and correct!
    pullDockerImage(dockerClient, os.getenv(
        'MYSQL_IMAGE'), os.getenv('MYSQL_VERSION'))

    # Update our compose file
    # If not, it'll abort!
    try:
        updateComposeFile("../stack/mysql/docker-compose.yml.template", "../stack/mysql/docker-compose.yml",
                          os.getenv('MYSQL_SERVICE_NAME'), os.getenv('MYSQL_IMAGE'), os.getenv('MYSQL_VERSION'))
    except:
        print(f"{pColors.FAIL}Cannot create the docker-compose.{pColors.ENDC}")
        abort()

    print("Buiding the image!")

    # Create the stack and deploy the service to our swarm
    # The SQL container will be on the manager node to store the data
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "../stack/mysql/docker-compose.yml", "local"])

    # Check if the container is successfully deployed!
    # If not, it'll abort
    if checkService(f"local_{os.getenv('MYSQL_SERVICE_NAME')}") == False:
        print(
            f"{pColors.FAIL}Cannot detect {os.getenv('MYSQL_SERVICE_NAME')} service!{pColors.ENDC}")
        abort()

    # If the container is doing great, it'll return the mysql root password to be used later.
    print(f"{pColors.OKGREEN}{os.getenv('MYSQL_SERVICE_NAME')} container created ! (1/4){pColors.ENDC}")
    return mysql_pwd
