#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"

# Defining the prod container names
prodBilling="prod_billing_app"
prodBillingDB="prod_billing_mysql"
prodWeight="prod_weight_app"
prodWeightDB="prod_my_sql_weight_db"

FLAG=false

# Function to check if a container is running or exists
check_container_running() {
    CONTAINER_NAME=$1

    # Check if the container is running (only running containers)
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" -q; then
        echo "Container ${CONTAINER_NAME} is already running."
    # Check if the container exists (even if stopped)
    elif docker ps -a --filter "name=^${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
        echo "Container ${CONTAINER_NAME} exists but is stopped."
        FLAG=true
    else
        FLAG=true
        echo "Container ${CONTAINER_NAME} is NOT running or does not exist."
    fi
}

# Check the status of each container
check_container_running "$prodBilling"
check_container_running "$prodBillingDB"
check_container_running "$prodWeight"
check_container_running "$prodWeightDB"

# If any container is not running, notify
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
