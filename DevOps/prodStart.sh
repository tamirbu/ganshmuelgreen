#!/bin/sh
main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"


git clone --single-branch --branch main https://github.com/tamirbu/ganshmuelgreen.git
cd $weight_folder
if [ $? -ne 0 ]; then
    echo "failed to enter '$weight_folder'"
    return 1
fi
docker-compose --env-file .env.prod build --no-cache
docker-compose --env-file .env.prod up --build -d
cd -

cd $billing_folder
if [ $? -ne 0 ]; then
    echo "failed to enter '$billing_folder'"
    return 1
fi
docker-compose --env-file .env.prod build --no-cache
docker-compose --env-file .env.prod up --build -d
cd -

cd $main_folder && echo "Removing $repo_folder..." %%rm -rf $repo_folder




