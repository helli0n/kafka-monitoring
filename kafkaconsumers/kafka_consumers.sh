#!/bin/sh

host1=`hostname -i`
curl1="curl -s http://$host1:8000/v3/kafka/local/consumer"
case $1 in
discovery)
           res=(`$curl1 | jq ".consumers[]" | tr -d '"'`)
             for element in ${res[@]}
              do
                 res1=`$curl1/$element/lag | jq 'if .status.group == "'${element}'" then .status.partitions[] | {"{#CONSUMER}":"'${element}'","{#PARTITION}":.partition,"{#TOPIC}":.topic} else 1 end'| jq -s add`
                    if [[ "$res1" != "null" ]]; then
                      ress_all=$ress_all,$res1
                    fi
             done
         ress_all=${ress_all:1}
         echo "{\"data\":[$ress_all]}"
     ;;
     consumer_status)
              res=`$curl1/$2/status | jq ".status.status" | tr -d '"'`
              case $res in
              NOTFOUND)
                echo 0
              ;;
              OK)
                echo 1
              ;;
              WARN)
                echo 2
              ;;
              ERR)
                echo 3
              ;;
              STOP)
                echo 4
              ;;
              STALL)
                echo 5
              ;;
              *) 
                echo $res
              esac
    ;;
    consumer_tottallag)
       res=`$curl1/$2/status | jq .status.totallag`
       echo $res
    ;;
    consumer_offsets)
           case $3 in 
           start)
              res=`$curl1/$2/lag | jq '.status.partitions[]' | jq 'if .topic == "'$5'" then . else null end' | grep -v null | jq 'if .partition == '$4' then .start.offset else null end' | grep -v null`
           ;;
           end)
              res=`$curl1/$2/lag | jq '.status.partitions[]' | jq 'if .topic == "'$5'" then . else null end' | grep -v null | jq 'if .partition == '$4' then .end.offset else null end' | grep -v null`
           ;;
           esac
           echo $res
     ;;
     consumer_lag)           
           case $3 in
           start)
              res=`$curl1/$2/lag | jq '.status.partitions[]' | jq 'if .topic == "'$5'" then . else null end' | grep -v null | jq 'if .partition == '$4' then .start.lag else null end' | grep -v null`
           ;;
           end)
              res=`$curl1/$2/lag | jq '.status.partitions[]' | jq 'if .topic == "'$5'" then . else null end' | grep -v null | jq 'if .partition == '$4' then .end.lag else null end' | grep -v null`
           ;;
           esac
           echo $res
     ;;
     consumer_offsets_status)
             res=`$curl1/$2/lag | jq '.status.partitions[]' | jq 'if .topic == "'$4'" then . else null end' | grep -v null | jq 'if .partition == '$3' then .status else null end' | grep -v null | tr -d '"'`
             case $res in
             NOTFOUND)
               echo 0
             ;;
             OK)
               echo 1
             ;;
             WARN)
               echo 2
             ;;
             ERR)
               echo 3
             ;;
             STOP)
               echo 4
             ;;
             STALL)
               echo 5
             ;;
             *)
             echo $res
             ;;
             esac
     ;;
     *)
           echo "Try
./kafka_consumers.sh discovery - use for discovery consumers and partitions
./kafka_consumers.sh consumer_status {#CONSUMER}
./kafka_consumers.sh consumer_tottallag {#CONSUMER}
./kafka_consumers.sh consumer_offsets {#CONSUMER} start|end {#PARTITION} {#TOPIC}
./kafka_consumers.sh consumer_lag {#CONSUMER} start|end {#PARTITION} {#TOPIC}
"
           ;;

esac