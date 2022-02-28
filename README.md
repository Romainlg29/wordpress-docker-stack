
# Wordpress stack (Automatic deployment)

An automatic Wordpress stack with Docker Swarm



## Installation

To run this deployment, you must install the following packages.

```bash
  apt install curl tar docker docker-compose
  
  pip install docker # Or run install-python-modules.sh
  pip install python-dotenv
```
    
## Deployment

To deploy this project run

```bash
  chmod +x init.sh
  ./init.sh
```

Then follow the instructions provided by the program.

### Deploy a new wordpress

To deploy a new wordpress, simply run the following file after completed the init setup

```bash
  chmod +x deploy-new-wordpress.sh
  ./deploy-new-wordpress.sh
```

Then follow the instructions provided by the program.


## Roadmap

- Scaling

- SSL support with let's encrypt
