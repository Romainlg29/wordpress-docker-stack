import string
import subprocess
import os

from utils import getResponse, pColors, getPassword, generateSecurePassword, checkService, pullDockerImage, abort


def create_nginx_container(dockerClient, root_secret: string):

    # Replace dots to underscore and lower the string
    # This is going to be used as service name
    def replace_dots_to_lower(s: string):
        return s.replace(".", "_").lower()

    # Check if it's a valid domain name

    def check_domain_length():
        domain_url = getResponse("Enter your domain URL (Ex: google.fr): ")
        if len(domain_url) < 3:  # Restricted as *.*
            print(f'{pColors.FAIL}Enter a valid domain!{pColors.ENDC}')
            return check_domain_length()
        else:
            return domain_url

    # Fetch the latest Wordpress build from the official repo
    # Then, it'll be extracted and moved to the target dir
    # We're also removing some useless files

    def get_latest_wordpress_build():
        subprocess.run(["curl", "-sO", "https://wordpress.org/latest.tar.gz",
                       "--output-dir", "./vols/websites/template"])
        subprocess.run(["tar", "-xf", "./vols/websites/template/latest.tar.gz",
                       "-C", "./vols/websites/template"])
        subprocess.run(["rm", "./vols/websites/template/latest.tar.gz",
                       "./vols/websites/template/wordpress/xmlrpc.php", "./vols/websites/template/wordpress/wp-config-sample.php"])
        subprocess.run(["chown", "-R", "www-data:www-data",
                       "./vols/websites/template/wordpress"])

    # Here we're getting our mysql container
    # Then, a new user and database will be created

    def create_database_entries(user_pwd: string, domain_url: string):
        dockerClient.containers.list(filters={"name": f"local_{os.getenv('MYSQL_SERVICE_NAME')}"})[0].exec_run(
            f'mysql -u root -p{root_secret} -e "CREATE DATABASE {domain_url};CREATE USER \'{domain_url}\'@\'%\' IDENTIFIED BY \'{user_pwd}\';GRANT ALL PRIVILEGES ON {domain_url}.* TO \'{domain_url}\'@\'%\' ;COMMIT;"')

    # Create the website volumes
    # Copying the wordpress template inside
    # And creating the NGINX config

    def create_domain_conf(user_pwd: string, domain_url: string):
        subprocess.run(["cp", "-a", "./vols/websites/template",
                       f"./vols/websites/{domain_url}"])

        # NGINX conf
        subprocess.run(["mkdir", f"./vols/websites/{domain_url}/nginx"])
        f = open(f"./configs/nginx/template.conf", "r+")
        o = open(f"./vols/websites/{domain_url}/nginx/default.conf", "wt")

        for l in f:
            o.write(l.replace('{DOMAIN_URL}', domain_url))
        f.close()
        o.close()

        # WP CONFIG
        f = open(f"./configs/wordpress/wp-config.php", "r+")
        o = open(f"./vols/websites/{domain_url}/wordpress/wp-config.php", "wt")

        for l in f:
            o.write(l.replace('{DB_NAME}', domain_url).replace(
                '{DB_USERNAME}', domain_url).replace('{DB_PASSWORD}', user_pwd).replace('{DB_SERVICE}', f"local_{os.getenv('MYSQL_SERVICE_NAME')}"))
        f.close()
        o.close()

    # Create the compose file
    # Replace all the placeholders

    def create_compose_file(domain_url: string):
        f = open(f"./stack/nginx/docker-compose.yml.template", "r+")
        o = open(f"./vols/websites/{domain_url}/docker-compose.yml", "wt")

        for l in f:
            o.write(l.replace('{DOMAIN_NAME}', domain_url).replace(
                '{DOMAIN_URL}', domain_url.replace("_", ".")).replace('{NAME}', os.getenv('NGINX_IMAGE')).replace('{TAG}', os.getenv('NGINX_VERSION')))
        f.close()
        o.close()

    # Deploy the service

    def deploy(domain_url: string):

        pullDockerImage(dockerClient, os.getenv(
            'NGINX_IMAGE'), os.getenv('NGINX_VERSION'))

        print("Buiding the image!")

        # Create the stack and deploy the service to our swarm
        # The SQL container will be on the manager node to store the data
        subprocess.run(["docker", "stack", "deploy", "-c",
                       f"./vols/websites/{domain_url}/docker-compose.yml", "content"])

        # Check if the container is successfully deployed!
        # If not, it'll abort
        if checkService(dockerClient, f"content_{domain_url}") == False:
            print(
                f"{pColors.FAIL}Cannot detect the NGINX service!{pColors.ENDC}")
            abort()

        print(f"{pColors.OKGREEN}NGINX container created ! (3/4){pColors.ENDC}")

    print(f"{pColors.HEADER}Creating the {os.getenv('NGINX_IMAGE')} container (3/4){pColors.ENDC}")

    # Get wordpress from the official repo
    get_latest_wordpress_build()

    print("You've to enter a root password, leave blank to generate a 64 characters password.")
    print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")

    # Ask for a password
    # If empty, it'll generate a secure one and return it to the user
    # It must be saved!
    mysql_pwd = getPassword()
    if mysql_pwd == "":
        mysql_pwd = generateSecurePassword()
        print(
            f"The domain password to access to the database is:{pColors.OKCYAN} {mysql_pwd}{pColors.ENDC}, please keep it secret!")

    # Generate the domain service name
    domain_url = replace_dots_to_lower(check_domain_length())

    # Create the user and the database
    create_database_entries(mysql_pwd, domain_url)

    # Create all the needed configs
    create_domain_conf(mysql_pwd, domain_url)

    # Creathe the compose file
    create_compose_file(domain_url)

    # Deploy the service
    deploy(domain_url)
