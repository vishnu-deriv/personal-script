#!/bin/bash

# Getting List of production servers
knife search node "tags:env_production" | grep Node > list_of_servers
sed 's/Node Name:   \|//' list_of_servers > list_of_servers2

# # Delete file "provider" if it exist
# file="provider"
# if [ -f "provider" ] ; then
#     rm "provider"
# fi


for (( c=1; c<=$(cat list_of_servers2 | wc -l ); c++ ))
do
mkdir -p servers
serverName=$(head -$c list_of_servers2 | tail -1)
# knife node show $serverName -l --format json | jq '.automatic.cloud.provider' >> provider

if [[ "$serverName" =~ .*"-".* ]]; then
test=$( echo ${serverName} | cut -d "-" -f 1 ) 
echo $test
touch servers/$test
knife node show ${serverName} -a hostname -a gce.instance.machineType -a cloud.public_ipv4 -a cloud.local_ipv4 -a cloud.provider -a gce.project.attributes.google-compute-default-region -a ec2.instance_type -a ec2.region -a alibaba.meta_data.instance_.instance_type -a alibaba.meta_data.region_id -F json >> servers/$test
else
knife node show ${serverName} -a hostname -a gce.instance.machineType -a cloud.public_ipv4 -a cloud.local_ipv4 -a cloud.provider -a gce.project.attributes.google-compute-default-region -a ec2.instance_type -a ec2.region -a alibaba.meta_data.instance_.instance_type -a alibaba.meta_data.region_id -F json >> servers/general_servers

# zone_print ${i} general
# aws ec2 describe-instances --filters "Name=tag:Name,Values=${serverName}" --query "Reservations[*].Instances[*].{Pub:PublicIpAddress,Private:PrivateIpAddress,Type:InstanceType,Status:State.Name}" --output text --region ${i} >> servers/general_servers

fi
done


# cat provider | sort | uniq



# # type =  ${serverName} | cut -d "-" -f 1 
# # echo $type
# # test -f $type || touch $type
# # touch "${type}"
# rm -r servers
# for (( c=1; c<=$(cat test1 | wc -l ); c++ ))
# do
# mkdir -p servers
# serverName=$(head -$c test1 | tail -1)

# echo $serverName
# if [[ "$serverName" =~ .*"-".* ]]; then
# test=$( echo ${serverName} | cut -d "-" -f 1 ) 
# echo $test
# touch servers/$test
# echo ${serverName} >> servers/$test

# else
# echo ${serverName} >> servers/general_servers


# fi
# # test -f $type || touch $type
# # touch "${type}"
# done