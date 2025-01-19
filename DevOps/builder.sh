#!/bin/sh
main_folder="ganshmuelgreen"
declare -A branch_to_folder
branch_to_folder["billing"]="$main_folder/Billing"
branch_to_folder["weight"]="$main_folder/Weight"
branch_to_folder["main"]="$main_folder"

# Check if a branch name is provided
if [ -z "$1" ]; then
  echo "Please provide a branch name."
  exit 1
fi
# Assign the first argument to the branch_name variable
branch_name=$1

git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git

if [ $? -ne 0 ]; then
  echo "Failed to clone branch: $branch_name"
  exit 1
fi

case "$branch_name" in
    "main")
        echo 'Branch is main'
        docker-compose -f main-docker-compose.yml -f $main_folder/Billing/docker-compose.yml -f $main_folder/Weight/docker-compose.yml up
        ;;
    "devops")
        echo 'DevOps is not autotically built and deployed'
        ;;
    "billing")
        echo "Branch is Billing"
        docker-compose -f "$main_folder/Billing/docker-compose.yml" up
        if [ $? -ne 0 ]; then
            echo "Failed to build Docker image: test-img-$branch_name"
            exit 1
        fi
        ;;
    "weight")
        echo "Branch is Weight"
        docker compose -f "$main_folder/Weight/docker-compose.yml" up
        if [ $? -ne 0 ]; then
            echo "Failed to build Docker image: test-img-$branch_name"
            exit 1
        fi
        ;;
    *)
        echo "Unknown branch name: $branch_name"
        exit 1
        ;;
esac
echo "Script executed successfully!"