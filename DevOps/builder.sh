#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"

# Check if a branch name is provided
if [ -z "$1" ]; then
  echo "Please provide a branch name."
  exit 1
fi

#The Email of the github user who made a pull request
gitMail=$2
# Assign the first argument to the branch_name variable
branch_name=$1
echo "branch is '$branch_name'"


if [ $? -ne 0 ]; then
  echo "Failed to clone branch: $branch_name"
  exit 1
fi

case "$branch_name" in
    "main")
        # cd $repo_folder
        # docker-compose -p prod -f main-docker-compose.yml up --force-recreate --env-file .env.prod up
        git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git
        cd $weight_folder
        docker-compose --env-file .env.test up -d
        cd $billing_folder
        docker-compose --env-file .env.test up -d
        # Run E2E tests
        cd $billing_folder
        docker-compose --env-file .env.test down
        cd $weight_folder
        docker-compose --env-file .env.test down
        # if success:
         #mailer.py (message to send, gitMail)
            cd $weight_folder
            docker-compose --env-file .env.prod up -d 
            cd $billing_folder
            docker-compose --env-file .env.prod up -d
        # else:
        #mailer.py (message to send, gitMail)
            # send mail to pusher + devops
        ;;
    "devops")
        echo 'devops is not automatically built and deployed'
        ;;
    "billing"|"weight")
        git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git
        cd $weight_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        cd $billing_folder
        docker-compose -p test up -d --force-recreate --env-file .env.test up
        # Run E2E tests
        # if success:
            #mailer.py (message to send, gitMail)
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