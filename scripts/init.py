import docker

from utils import pColors
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

    # Create a MYSQL service, the image can be changed via .env file
    # Return our root secret, it'll be used later
    root_secret = create_mysql_container(dockerClient)

    # Create a PHP service, as well, the image can be changed
    # However, if you change, please make sure that you have all the wordpress ext within!
    create_php_container(dockerClient)

    # Create the default NGINX service
    # It comes with Wordpress
    create_nginx_container(dockerClient, root_secret)

    # Finally the traefik container
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


# Create the swarm network and return the key
# The returned key can be used to connect other servers
create_swarm(dockerClient)

# Create three networks web, content, local
# Web is used by Traefik and every NGINX services
# Content is used by every NGINX services and PHP
# Local is used PHP and MariaDB
create_networks(dockerClient)

# Create all the default container
# It follows the INIT setup
init_containers()


# Finally
print(f"{pColors.OKGREEN + pColors.BOLD}The deployment was successful!{pColors.ENDC}")

