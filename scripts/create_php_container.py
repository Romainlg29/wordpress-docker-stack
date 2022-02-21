import os
import subprocess

from abort import abort
from utils import pColors, checkService, pullDockerImage, updateComposeFile


def create_php_container(dockerClient):

    print(f"{pColors.HEADER}Creating the {os.getenv('PHP_IMAGE')} container (2/4){pColors.ENDC}")

    # Here' we're pulling the needed image from Docker Hub
    # Image name comes from the .env file
    # It must be filled and correct!
    pullDockerImage(dockerClient, os.getenv(
        'PHP_IMAGE'), os.getenv('PHP_VERSION'))

    # Update our compose file
    # If not, it'll abort!
    try:
        updateComposeFile("../stack/php/docker-compose.yml.template", "../stack/php/docker-compose.yml",
                          os.getenv('PHP_SERVICE_NAME'), os.getenv('PHP_IMAGE'), os.getenv('PHP_VERSION'))
    except:
        print(f"{pColors.FAIL}Cannot create the docker-compose.{pColors.ENDC}")
        abort()

    print("Buiding the image!")

    # Create the stack and deploy the service to our swarm
    # This service must access to every nginx volumes
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "../stack/php/docker-compose.yml", "local"])

    # Check if the container is successfully deployed!
    # If not, it'll abort
    if checkService(dockerClient, f"local_{os.getenv('PHP_SERVICE_NAMe')}") == False:
        print(
            f"{pColors.FAIL}Cannot detect the {os.getenv('PHP_SERVICE_NAME')} service!{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}{os.getenv('PHP_SERVICE_NAME')} container created ! (2/4){pColors.ENDC}")
