#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/Weight"

# Check if a branch name is provided
if [ -z "$1" ]; then
  echo "Please provide a branch name."
  exit 1
fi
# Assign the first argument to the branch_name variable
branch_name=$1
echo "branch is '$branch_name'"
git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git

if [ $? -ne 0 ]; then
  echo "Failed to clone branch: $branch_name"
  exit 1
fi

case "$branch_name" in
    "main")
        # cd $repo_folder
        # docker-compose -p prod -f main-docker-compose.yml up --force-recreate --env-file .env.prod up
        cd $weight_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        cd $billing_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        # Run E2E tests
        # docker-compose down all test containers
        cd $weight_folder
        docker-compose down
        cd $billing_folder
        docker-compose down
        
        # if success:
            cd $weight_folder
            docker-compose -p prod up -d --force-recreate --env-file .env.prod up
            cd $billing_folder
            docker-compose -p prod up -d --force-recreate --env-file .env.prod up
        # else:
            # send mail to pusher + devops
        ;;
    "devops")
        echo 'devops is not automatically built and deployed'
        ;;
    "billing"|"weight")
        cd $weight_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        cd $billing_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        # Run E2E tests
        # if success:
            # send success mail to pusher
        # else:
        #     send failure success to push

        # docker-compose down all test containers
        cd $weight_folder
        docker-compose down
        cd $billing_folder
        docker-compose down

        # if [ $? -ne 0 ]; then
        #     echo "Failed to build Docker image for $branch_name"
        #     exit 1
        # fi
        ;;
    *)
        echo "Unknown branch name: $branch_name"
        exit 1
        ;;
esac
cd $main_folder
echo "removing $repo_folder..."
rm -rf $repo_folder
echo "Script executed successfully!"