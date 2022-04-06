import docker
import sys

# get our Docker client
dockerClient = docker.from_env()

def auto_scaling(dockerClient):

    # Get the list of containers
    cList = dockerClient.containers.list()

    # Define a dict that will hold list all of services used by our containers
    # This will contain a dict with the following pattern
    # 'service' : {cpu_usage: 0, cpu_usage_mean: 0, replicas: 1}
    cgList = {}

    # Loop through all containers
    for container in cList:

        # Get the name of the container service
        service = container.attrs['Config']['Labels']['com.docker.swarm.service.name']

        try:

            # Append the contain cpu_usage to our service dict
            cpu_usage = container.stats(stream=False)['cpu_stats']['cpu_usage']['total_usage'] / container.stats(stream=False)['cpu_stats']['system_cpu_usage'] * 100
            cgList[service]['cpu_usage'] += cpu_usage

            # Add one to replicas
            cgList[service]['replicas'] += 1

        except KeyError:

            # Create a new service dict and append data
            cpu_usage = container.stats(stream=False)['cpu_stats']['cpu_usage']['total_usage'] / container.stats(stream=False)['cpu_stats']['system_cpu_usage'] * 100
            cgList[service] = {'cpu_usage': cpu_usage, 'cpu_usage_mean:': 0, 'replicas': 1}
            

    # Loop through all services
    for service in cgList:

        # Set the average cpu_usage for each service
        cgList[service]['cpu_usage_mean'] = cgList[service]['cpu_usage'] / cgList[service]['replicas']

        # If the average cpu_usage is greater than 70%
        if cgList[service]['cpu_usage_mean'] > 70:
                
            # Scale up the service
            dockerClient.services.get(service).scale(cgList[service]['replicas'] + 1)

            print(f"Scaled up {service} to {cgList[service]['replicas'] + 1}")

        # If the average cpu_usage is less than 30% and the replicas are greater than 1
        elif cgList[service]['cpu_usage_mean'] < 30 and cgList[service]['replicas'] > 1:

            # Scale down the service
            dockerClient.services.get(service).scale(cgList[service]['replicas'] - 1)

            print(f"Scaled down {service} to {cgList[service]['replicas'] - 1}")


if __name__ == "__main__":

    import docker
    import sys
    import time

    # Get sys args
    if len(sys.argv) > 1:

        if sys.argv[1] == '-h':

            print("\n")
            print("Usage: auto-scaling.py")
            print("Scales up or down services based on CPU usage (Swarm support)")
            print("Thresholds: < 30% on average service will scale down and 70% > will scale up")
            print("\n")
            print('Args:')
            print('-h: Prints this message')
            print("-t <seconds>: Time in seconds to wait before running the script again")
            print("\n")
            print("Recommended to run this script with cron")
            print("Ajust the timing to your needs")
            print("\n")
            sys.exit()


        # -t args refers to the time in seconds to wait before running the script again
        # It'll use a while loop which isn't the best to use
        # Consider using cron instead if you want to run this script every X minutes

        if sys.argv[1] == '-t':

            if sys.argv[2]:
                try:
                    interval = int(sys.argv[2])

                     # Get our Docker client
                    dockerClient = docker.from_env()

                    while True:

                        print(f"Running auto-scaling script every {interval} seconds")

                        # Call auto_scaling function
                        try:
                            auto_scaling(dockerClient)
                        except:
                            print("An error occured.")

                        # Wait for the interval    
                        time.sleep(interval)

                except ValueError:
                    print("Please enter a valid number")
                    sys.exit()

            else:
                print("Please enter a valid number")
                sys.exit()
    
    else:
        
        # Get our Docker client
        dockerClient = docker.from_env()

        # Call auto_scaling function
        try:
            auto_scaling(dockerClient)
        except:
            print("An error occured.")
