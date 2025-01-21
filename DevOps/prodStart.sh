#!/bin/sh


main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"


git clone --single-branch --branch main https://github.com/tamirbu/ganshmuelgreen.git
cd $weight_folder
docker-compose --env-file .env.prod up -d 
cd $billing_folder
docker-compose --env-file .env.prod up -d 
cd $main_folder
echo "removing $repo_folder..."
rm -rf $repo_folder