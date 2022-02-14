import secrets
import string
import docker
import subprocess


class pColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Docker client
dockerClient = docker.from_env()

# Swarm


def create_swarm():
    print('Creating the Swarm network!')
    try:
        k = dockerClient.swarm.init()
        print(f"Your swarm key is : {pColors.OKBLUE + k + pColors.ENDC}")
    except:
        print(f"{pColors.FAIL}Can't create the Swarm! Aborting{pColors.ENDC}")
        quit()

# Networks


def create_networks():
    print('Creating networks!')
    networks = []
    try:
        networks.append(dockerClient.networks.create(
            name="web", driver="overlay", attachable=True, check_duplicate=True))
        networks.append(dockerClient.networks.create(
            name="content", driver="overlay", attachable=True, check_duplicate=True))
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

# Passwords


def getPassword():
    try:
        return str(input("Enter a secure password: "))
    except:
        return getPassword()


def generateSecurePassword():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(64))


def getResponse(text: string):
    try:
        return str(input(text))
    except:
        return getResponse()

# Services


def checkService(service_id):
    try:
        dockerClient.services.get(service_id=service_id)
        return True
    except:
        return False

# Containers


def create_mysql_container():
    print('Creating Mysql container :')
    print("You've to enter a root password, leave blank to generate a 64 characters password.")
    print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")
    mysql_pwd = getPassword()
    if mysql_pwd == "":
        mysql_pwd = generateSecurePassword()
        print(f"Your root password is: {mysql_pwd}")

    try:
        dockerClient.secrets.create(name="mysql-root", data=mysql_pwd)
        print("Secret created!")
    except:
        print(f"{pColors.FAIL}Can't create a new secret... Aborting{pColors.ENDC}")
        quit()

    print("Pulling the image... (This can take few minutes.)")
    dockerClient.images.pull("mysql", "8")
    print("Buiding...")
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/mysql/docker-compose.yml", "local"])
    if checkService("local_mysql") == False:
        print(
            f"{pColors.FAIL}Cannot detect the Mysql service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}Mysql container created !{pColors.ENDC}")
    return mysql_pwd


def create_php_container():
    print('Creating PHP container : ')
    print("Pulling the image (This can take few minutes.)")
    dockerClient.images.pull("devilbox/php-fpm", "8.1-prod")
    print("Buiding...")
    subprocess.run(["docker", "stack", "deploy", "-c",
                    "./stack/php/docker-compose.yml", "local"])
    if checkService("local_php") == False:
        print(
            f"{pColors.FAIL}Cannot detect the PHP service! Aborting{pColors.ENDC}")
        quit()

    print(f"{pColors.OKGREEN}PHP container created !{pColors.ENDC}")


def create_nginx_container(root_secret: string):

    def replace_dots_to_lower(s: string):
        return s.replace(".", "_").lower()

    def check_domain_length():
        domain_url = getResponse("Enter your domain URL (Ex: google.fr): ")
        if len(domain_url) < 3:  # Restricted as *.*
            print(f'{pColors.FAIL}Enter a valid domain!{pColors.ENDC}')
            return check_domain_length()
        else:
            return domain_url

    def get_latest_wordpress_build():
        subprocess.run(["curl", "-O", "https://wordpress.org/latest.tar.gz",
                       "--output-dir", "./vols/websites/template"])
        subprocess.run(["tar", "-xf", "./vols/websites/template/latest.tar.gz",
                       "-C", "./vols/websites/template"])
        subprocess.run(["rm", "./vols/websites/template/latest.tar.gz",
                       "./vols/websites/template/wordpress/xmlrpc.php", "./vols/websites/template/wordpress/wp-config.php"])
        subprocess.run(["chown", "-R", "www-data:www-data",
                       "./vols/websites/template/wordpress"])

    def create_database_entries(user_pwd: string, domain_url: string):
        dockerClient.containers.list(filters={'name': 'local_mysql'})[0].exec_run(
            f'mysql -u root -p{root_secret} -e "CREATE DATABASE {domain_url};CREATE USER \'{domain_url}\'@\'%\' IDENTIFIED BY \'{user_pwd}\';GRANT ALL PRIVILEGE ON {domain_url}.* TO \'{domain_url}\'@\'%\' ;COMMIT;"')

    def create_domain_conf(user_pwd: string, domain_url: string):
        print(f'Creating {domain_url} folder.')
        subprocess.run(["cp", "-a", "./vols/websites/template",
                       f"./vols/websites/{domain_url}"])

        # NGINX conf
        subprocess.run(["mkdir", f"./vols/websites/{domain_url}/nginx"])
        f = open(f"./configs/nginx/template.conf", "r+")
        o = open(f"./vols/websites/{domain_url}/nginx/template.conf", "wt")

        for l in f:
            o.write(l.replace('{DOMAIN_URL}', domain_url))
        f.close()
        o.close()

        # WP CONFIG
        f = open(f"./configs/wordpress/wp-config.php", "r+")
        o = open(f"./vols/websites/{domain_url}/wordpress/wp-config.php", "wt")

        for l in f:
            o.write(l.replace('{DB_NAME}', domain_url).replace(
                '{DB_USERNAME}', domain_url).replace('{DB_PASSWORD}', user_pwd))
        f.close()
        o.close()

    def create_compose_file(domain_url: string):
        f = open(f"./stack/nginx/docker-compose.yml", "r+")
        o = open(f"./vols/websites/{domain_url}/docker-compose.yml", "wt")

        for l in f:
            o.write(l.replace('{DOMAIN_NAME}', domain_url).replace(
                '{DOMAIN_URL}', domain_url.replace("_", ".")))
        f.close()
        o.close()

    def deploy(domain_url: string):
        print("Pulling the image (This can take few minutes.)")
        dockerClient.images.pull("nginx", "1.21.6")
        print("Buiding...")
        subprocess.run(["docker", "stack", "deploy", "-c",
                       f"./vols/websites/{domain_url}/docker-compose.yml", "content"])
        if checkService(f"content_{domain_url}") == False:
            print(
                f"{pColors.FAIL}Cannot detect the NGINX service! Aborting{pColors.ENDC}")
            quit()

        print(f"{pColors.OKGREEN}NGINX container created !{pColors.ENDC}")

    print('Creating NGINX container:')
    print('Getting wordpress...')
    get_latest_wordpress_build()
    print("You've to enter a password, leave blank to generate a 64 characters password. It'll be used as your mysql secret.")
    print(f"{pColors.WARNING}Specials characters aren't allowed !{pColors.ENDC}")
    mysql_pwd = getPassword()
    if mysql_pwd == "":
        mysql_pwd = generateSecurePassword()
        print(f"Your root password is: {mysql_pwd}")
    domain_url = replace_dots_to_lower(check_domain_length())
    create_database_entries(mysql_pwd, domain_url)
    create_domain_conf(mysql_pwd, domain_url)
    create_compose_file(domain_url)
    deploy(domain_url)


def init_containers():
    print('Creating containers!')
    root_secret = create_mysql_container()
    create_php_container()
    create_nginx_container(root_secret)


# INIT
#
# 1. Create the swarm and returnting the key to the user
# 2. Create all the needed networks (WEB, CONTENT, LOCAL)
# 3. Create containers
#    3.1 Pull and deploy the Mysql container
#    3.2 Pull and deploy the PHP container
#    3.3 Pull and deploy the base NGINX container
#    3.4 Pull and deploy the traefik container
# 4. Done!


create_swarm()
create_networks()


init_containers()
