import subprocess
from utils import pColors, checkService

def create_php_container(dockerClient):
    print('Creating PHP container : ')
    print("Pulling the image (This can take few minutes.)")
    dockerClient.images.pull("devilbox/php-fpm", "8.1-prod")
    print("Buiding...")
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/php/docker-compose.yml", "local"])
    if checkService(dockerClient, "local_php") == False:
        print(
            f"{pColors.FAIL}Cannot detect the PHP service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}PHP container created !{pColors.ENDC}")