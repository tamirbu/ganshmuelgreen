#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"

#defining the prod container names
prodBilling="prod_billing_app"
prodBillingDB="prod_billing_mysql"
prodWeight="prod_weight_app"
prodWeightDB="prod_my_sql_weight_db"

FLAG=false


check_container_running() {
    CONTAINER_NAME=$1
    # Check if the container is running
    if docker ps --filter "name=${CONTAINER_NAME}" --filter "status=running" -q; then
        echo "Container ${CONTAINER_NAME} is already running."
    else
        FLAG=true
        echo "Container ${CONTAINER_NAME} is NOT running."
        # Optionally, start the container if not running
        # docker-compose up -d ${CONTAINER_NAME}
    fi
}

check_container_running "$prodBilling"
check_container_running "$prodBillingDB"
check_container_running "$prodWeight"
check_container_running "$prodWeightDB"


if [ "$FLAG" = true ]; then
    echo "One or more containers of prod environment are not running!"
    git clone --single-branch --branch main https://github.com/tamirbu/ganshmuelgreen.git
    cd $weight_folder
    docker-compose --env-file .env.prod up -d 
    cd $billing_folder
    docker-compose --env-file .env.prod up -d 
    cd $main_folder
    echo "removing $repo_folder..."
    rm -rf $repo_folder
    
else
    echo "Prod environment is already up!"
fi



