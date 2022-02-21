import string
import subprocess

from utils import getResponse, pColors, getPassword, generateSecurePassword

def create_nginx_container(dockerClient, root_secret: string):

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
            f'mysql -u root -p{root_secret} -e "CREATE DATABASE {domain_url};CREATE USER \'{domain_url}\'@\'%\' IDENTIFIED BY \'{user_pwd}\';GRANT ALL PRIVILEGES ON {domain_url}.* TO \'{domain_url}\'@\'%\' ;COMMIT;"')

    def create_domain_conf(user_pwd: string, domain_url: string):
        print(f'Creating {domain_url} folder.')
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