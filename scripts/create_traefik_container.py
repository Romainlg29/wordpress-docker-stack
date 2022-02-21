import subprocess
import os

from abort import abort

from utils import pColors, checkService, pullDockerImage, updateComposeFile

def create_traefik_container(dockerClient):

    print(f"{pColors.HEADER}Creating the {os.getenv('MYSQL_IMAGE')} container (4/4){pColors.ENDC}")


    # Here' we're pulling the needed image from Docker Hub
    # Image name comes from the .env file
    # It must be filled and correct!
    pullDockerImage(dockerClient, os.getenv('TREAFIK_IMAGE'), os.getenv('TRAEFIK_VERSION'))


    # Update our compose file
    # If not, it'll abort!
    try:
        updateComposeFile("../stack/traefik/docker-compose.yml.template", "../stack/traefik/docker-compose.yml",
                          os.getenv('TRAEFIK_SERVICE_NAME'), os.getenv('TRAEFIK_IMAGE'), os.getenv('TRAEFIK_VERSION'))
    except:
        print(f"{pColors.FAIL}Cannot create the docker-compose.{pColors.ENDC}")
        abort()

    print("Buiding the image!")

    # Create the stack and deploy the service to our swarm
    # This service doesn't require any placement on nodes
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "../stack/traefik/docker-compose.yml", "web"])


    # Check if the container is successfully deployed!
    # If not, it'll abort
    if checkService("web_traefik") == False:
        print(
            f"{pColors.FAIL}Cannot detect the Traefik service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}{os.getenv('TRAEFIK_SERVICE_NAME')} container created ! (4/4){pColors.ENDC}")