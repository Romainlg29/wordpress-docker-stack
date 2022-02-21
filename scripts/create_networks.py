from utils import pColors

def create_networks(dockerClient):
    print('Creating networks!')
    networks = []
    try:
        networks.append(dockerClient.networks.create(
            name="web", driver="overlay", attachable=True, check_duplicate=True))
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