import docker

from utils import pColors, generateSecurePassword, getPassword, getResponse
from dotenv import load_dotenv

import create_swarm
import create_networks
import create_nginx_container
import create_php_container
import create_traefik_container
import create_mysql_container


# Get our env variables
load_dotenv()
# get our Docker client
dockerClient = docker.from_env()



def init_containers():
    print(f'{pColors.HEADER}Welcome!{pColors.ENDC}')
    root_secret = create_mysql_container(dockerClient)
    create_php_container(dockerClient)
    create_nginx_container(dockerClient, root_secret)
    create_traefik_container(dockerClient)


# INIT
#
# 1. Create the swarm and returning the key to the user
# 2. Create all the needed networks (WEB, CONTENT, LOCAL)
# 3. Create containers
#    3.1 Pull and deploy the Mysql container
#    3.2 Pull and deploy the PHP container
#    3.3 Pull and deploy the base NGINX container
#    3.4 Pull and deploy the traefik container
# 4. Done!


create_swarm(dockerClient)
create_networks(dockerClient)


init_containers()
