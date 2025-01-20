#!/bin/sh


main_folder="/app"
repo_folder="$main_folder/ganshmuelgreen"
billing_folder="$repo_folder/Billing"
weight_folder="$repo_folder/weight_team"




cd $weight_folder
docker-compose --env-file .env.prod up -d 
cd $billing_folder
docker-compose --env-file .env.prod up -d 