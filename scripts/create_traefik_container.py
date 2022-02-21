import subprocess
import os

from utils import pColors, checkService, pullDockerImage, updateComposeFile, abort

def create_traefik_container(dockerClient):

    print(f"{pColors.HEADER}Creating the {os.getenv('TRAEFIK_IMAGE')} container (4/4){pColors.ENDC}")


    # Here' we're pulling the needed image from Docker Hub
    # Image name comes from the .env file
    # It must be filled and correct!
    pullDockerImage(dockerClient, os.getenv('TRAEFIK_IMAGE'), os.getenv('TRAEFIK_VERSION'))


    # Update our compose file
    # If not, it'll abort!
    try:
        updateComposeFile("./stack/traefik/docker-compose.yml.template", "./stack/traefik/docker-compose.yml",
                          os.getenv('TRAEFIK_SERVICE_NAME'), os.getenv('TRAEFIK_IMAGE'), os.getenv('TRAEFIK_VERSION'))
    except:
        print(f"{pColors.FAIL}Cannot create the docker-compose.{pColors.ENDC}")
        abort()

    print("Buiding the image!")

    # Create the stack and deploy the service to our swarm
    # This service doesn't require any placement on nodes
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/traefik/docker-compose.yml", "web"])


    # Check if the container is successfully deployed!
    # If not, it'll abort
    if checkService(dockerClient, f"web_{os.getenv('TRAEFIK_SERVICE_NAME')}") == False:
        print(
            f"{pColors.FAIL}Cannot detect {os.getenv('TRAEFIK_SERVICE_NAME')} service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}{os.getenv('TRAEFIK_SERVICE_NAME')} container created ! (4/4){pColors.ENDC}")