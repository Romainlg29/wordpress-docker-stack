from utils import pColors

def create_swarm(dockerClient):
    print('Creating the Swarm network!')
    try:
        k = dockerClient.swarm.init()
        print(f"Your swarm key is : {pColors.OKBLUE + k + pColors.ENDC}")
    except:
        print(f"{pColors.FAIL}Can't create the Swarm! Aborting{pColors.ENDC}")
        quit()
