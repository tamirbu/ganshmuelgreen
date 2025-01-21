#!/bin/sh

# Set your project name as 'prod'
PROJECT_NAME="prod"  # This is the specific environment you're interested in

# Define the container names using the PROJECT_NAME variable
CONTAINER_BILLING="${PROJECT_NAME}_billing_app"
CONTAINER_BILLING_DB="${PROJECT_NAME}_billing_mysql"
CONTAINER_WEIGHT="${PROJECT_NAME}_weight_app"
CONTAINER_WEIGHT_DB="${PROJECT_NAME}_my_sql_weight_db"

# Function to check if a container is running
check_container_running() {
    CONTAINER_NAME=$1

    # Check if the container is running using docker ps
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" -q; then
        echo "Container ${CONTAINER_NAME} is already running."
    else
        echo "Container ${CONTAINER_NAME} is NOT running."
        return 1  # Indicate that a container is not running
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

