#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"

# Define the base names of the prod containers
prodBilling="prod_billing_app"
prodBillingDB="prod_billing_mysql"
prodWeight="prod_weight_app"
prodWeightDB="prod_my_sql_weight_db"

# Flag to track container status
FLAG=false

# Get the project name from the current directory or from environment
# This assumes you're running the script from the project root where docker-compose.yml is located
PROJECT_NAME=$(basename "$PWD")

# Function to check if a container is running or exists
check_container_running() {
    CONTAINER_NAME=$1
    echo "Checking for container ${CONTAINER_NAME}..."

    # Construct the full container name using project name and service name
    FULL_CONTAINER_NAME="${PROJECT_NAME}_${CONTAINER_NAME}_1"
    echo "Looking for container: ${FULL_CONTAINER_NAME}"

    # List all containers (including stopped ones) and check if any match the full container name
    container_list=$(docker ps -a --format '{{.Names}}')

    # Debug: print out all containers to see what we are working with
    echo "All containers: $container_list"

    # Check if the container is running (only running containers)
    if docker ps --filter "name=^${FULL_CONTAINER_NAME}$" --filter "status=running" -q; then
        echo "Container ${FULL_CONTAINER_NAME} is already running."
    # Check if the container exists (even if stopped)
    elif echo "$container_list" | grep -q "^${FULL_CONTAINER_NAME}$"; then
        echo "Container ${FULL_CONTAINER_NAME} exists but is stopped."
        FLAG=true
    else
        FLAG=true
        echo "Container ${FULL_CONTAINER_NAME} is NOT running or does not exist."
    fi
}

# Check the status of each container
check_container_running "$prodBilling"
check_container_running "$prodBillingDB"
check_container_running "$prodWeight"
check_container_running "$prodWeightDB"

# If any container is not running, notify and deploy
if [ "$FLAG" = true ]; then
    echo "One or more containers of prod environment are not running!"
    git clone --single-branch --branch main https://github.com/tamirbu/ganshmuelgreen.git
    cd $weight_folder
    docker-compose --env-file .env.prod up -d 
    cd $billing_folder
    docker-compose --env-file .env.prod up -d 
    cd $main_folder
    echo "Removing $repo_folder..."
    rm -rf $repo_folder
else
    echo "Prod environment is already up!"
fi

