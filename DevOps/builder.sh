#!/bin/sh
main_folder="ganshmuelgreen"
# Check if a branch name is provided
if [ -z "$1" ]; then
  echo "Please provide a branch name."
  exit 1
fi
# Assign the first argument to the branch_name variable
branch_name=$1
# Checkout the specified branch
#git checkout "$branch_name"
#if [ $? -ne 0 ]; then
  #echo "Failed to checkout branch: $branch_name"
  #exit 1
#fi
# Pull the latest changes from the specified branch
git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git
if [ $? -ne 0 ]; then
  echo "Failed to pull branch: $branch_name"
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
        docker compose -f "$main_folder/Billing/docker-compose.yml" up
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
# Build the Docker image
#docker compose up -d -t "test-$branch_name"
#if [ $? -ne 0 ]; then
  #echo "Failed to build Docker image: test-img-$branch_name"
  #exit 1
#fi
# Run the Docker container
docker run -it --name testdocker-$branch_name -d "test-img-$branch_name"
if [ $? -ne 0 ]; then
  echo "Failed to run Docker container: testdocker"
  exit 1
fi
echo "Script executed successfully!"