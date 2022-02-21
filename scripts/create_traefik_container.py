import subprocess
from utils import pColors, checkService

def create_traefik_container(dockerClient):
    print('Creating Traefik container : ')
    print("Pulling the image (This can take few minutes.)")
    dockerClient.images.pull("traefik", "2.6")
    print("Buiding...")
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/traefik/docker-compose.yml", "web"])
    if checkService("web_traefik") == False:
        print(
            f"{pColors.FAIL}Cannot detect the Traefik service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}Traefik container created !{pColors.ENDC}")