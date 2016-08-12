# Welcome to the kafka-monitoring wiki!

## First you have to install zabbix-java-gataway
    yum install -y zabbix-java-gataway
## Configuring zabbix-java-gataway
    mcedit /etc/zabbix/zabbix_java_gateway.conf
Uncoment and set **START_POLLERS=10**
## Configuring zabbix-server
    mcedit /etc/zabbix/zabbix_server.conf
Uncoment and set to **StartJavaPollers=5**
Change IP for **JavaGateway=IP_address_java_gateway**
## Restart zabbix-server
    /etc/init.d/zabbix-java-gataway restart
## Add to autorun zabbix-java-gataway
     chkconfig --level 345 zabbix-java-gataway on
## Start zabbix-java-gataway
    /etc/init.d/zabbix-java-gataway start
## Kafka configuration

    cd /opt/kafka/bin
    mcedit kafka-run-class.sh

change from

    # JMX settings
    if [ -z "$KAFKA_JMX_OPTS" ]; then
    KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -   Dcom.sun.management.jmxremote.ssl=false "
    fi

to

    # JMX settings
    if [ -z "$KAFKA_JMX_OPTS" ]; then
    KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=12345 -    Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false "
    fi
## Add Kafka as service

Add to /etc/supervisord.conf that lines

     [program:kafka]
     command=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
     directory=/opt/kafka/
     autostart=true
     autorestart=true
     stopasgroup=true
     startsecs=10
     startretries=999
     log_stdout=true
     log_stderr=true
     logfile=/var/log/kafka/supervisord-kafka.out
     logfile_maxbytes=20MB
     logfile_backups=10
## Restart supervisor 
     /etc/init.d/supervisord restart
# Zabbix configuration

#Upload scripts for discovery JMX

     git clone https://github.com/helli0n/kafka-monitoring.git 
     cd zabbix/kafka
     cp jmx_discovery /etc/zabbix/externalscripts
     cp JMXDiscovery-0.0.1.jar etc/zabbix/externalscripts

##Import template
Log in to your zabbix web

**Click Configuration->Templates->Import**

Download template [zbx_kafka_templates.xml](https://github.com/helli0n/kafka-monitoring/blob/master/zbx_kafka_templates.xml) and upload to zabbix
Then add this template to Kafka and configure JMX interfaces on zabbix 

Enter Kafka IP address and JMX port
If you see jmx icon, you configured JMX monitoring  good!

# Troubles 
if you have problems you can check JMX using this script
     #!/usr/bin/env bash
     
     ZBXGET="/usr/bin/zabbix_get"
     if [ $# != 5 ]
     then
     echo "Usage: $0 <JAVA_GATEWAY_HOST> <JAVA_GATEWAY_PORT> <JMX_SERVER> <JMX_PORT> <KEY>"
     exit;
     fi
     QUERY="{\"request\": \"java gateway jmx\",\"conn\": \"$3\",\"port\": $4,\"keys\": [\"$5\"]}"
     $ZBXGET -s $1 -p $2 -k "$QUERY"

**eg.:** ./zabb_get_java  zabbix-java-gateway-ip 10052 server-test-ip 12345 
'jmx[java.lang:type=Threading,PeakThreadCount]'


# kafka-monitoring
https://github.com/helli0n/kafka-monitoring/wiki/Kafka-monitoring

https://engineering.linkedin.com/apache-kafka/burrow-kafka-consumer-monitoring-reinvented

https://github.com/linkedin/Burrow/wiki

https://community.hortonworks.com/articles/28103/monitoring-kafka-with-burrow.html
