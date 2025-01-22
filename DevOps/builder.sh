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

docker_compose_build_n_up() {
    local folder=$1
    local env_filename=$2
    local project=$3
    cd $folder
    if [ $? -ne 0 ]; then
        echo "failed to enter '$folder'"
        return 1
    fi
    docker-compose --env-file "$env_filename" build --no-cache
    if [ $project -eq "test" ]; then
        docker-compose --env-file "$env_filename" -p $project up --build -d --no-recreate
    else
        docker-compose --env-file "$env_filename" -p $project up --build -d
    fi
    cd -
}

case "$branch_name" in
    "main")
        python3 mailer.py "Hello from the webserver" "$gitMail"
        git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git
        docker_compose_build_n_up $weight_folder .env.test test
        docker_compose_build_n_up $billing_folder .env.test test 
        # Run E2E tests
        cd $billing_folder && docker-compose --env-file .env.test -p test down
        cd $weight_folder && docker-compose --env-file .env.test -p test down
        # if success:
         #mailer.py (message to send, gitMail)
            cd $weight_folder && docker-compose --env-file .env.prod -p prod down && \
            docker_compose_build_n_up $weight_folder .env.prod prod
            cd $billing_folder && docker-compose --env-file .env.prod -p prod down && \
            docker_compose_build_n_up $billing_folder .env.prod prod
        # else:
        #mailer.py (message to send, gitMail)
            # send mail to pusher + devops
        ;;
    "devops")
        echo 'devops is not automatically built and deployed'
        python3 mailer.py "Hello, you pushed into Devops branch", "$gitMail"
        ;;
    "billing"|"weight")
        git clone --single-branch --branch $branch_name https://github.com/tamirbu/ganshmuelgreen.git
        docker_compose_build_n_up $weight_folder .env.test test
        docker_compose_build_n_up $billing_folder .env.test test 
        # Run E2E tests
        # if success:
        python3 mailer.py "Hello, you pushed into a branch on git", "$gitMail"
        # else:
        #     send failure success to push
        cd $billing_folder && docker-compose --env-file .env.test -p test down
        cd $weight_folder && docker-compose --env-file .env.test -p test down
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