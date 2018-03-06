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

## Kafka systemd unit

For systemd is possible to use unit like example below.
For this example kafka is installed in `/usr/local/kafka/kafka_2.11-1.0.0`

```
[Unit]
Description=Apache Kafka
Wants=network.target
After=network.target

[Service]
LimitNOFILE=32768
User=kafka

Environment=JAVA=/usr/bin/java
Environment="KAFKA_USER=kafka"
Environment="KAFKA_HOME=/usr/local/kafka/kafka_2.11-1.0.0"
Environment="SCALA_VERSION=2.11"
Environment="KAFKA_CONFIG=/usr/local/kafka/config"
Environment="KAFKA_BIN=/usr/local/kafka/bin"
Environment="KAFKA_LOG4J_OPTS=-Dlog4j.configuration=file:/usr/local/kafka/config/log4j.properties"
Environment="KAFKA_OPTS="
Environment="KAFKA_HEAP_OPTS=-Xmx512M -Xms256M"
Environment="KAFKA_JVM_PERFORMANCE_OPTS=-server -XX:+UseCompressedOops -XX:+UseParNewGC -XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled -XX:+CMSScavengeBeforeRemark -XX:+DisableExplicitGC -Djava.awt.headless=true"
Environment="KAFKA_LOG_DIR=/var/log/kafka"
Environment="KAFKA_JMX_OPTS=-Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.net.preferIPv4Stack=true -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.port=<REPLACE_WITH_YOUR_JMX_PORT> -Dcom.sun.management.jmxremote.rmi.port=<REPLACE_WITH_YOUR_JMX_PORT> -Djava.rmi.server.hostname=<REPLACE_WITH_YOUR_HOSTNAME>"

ExecStart=/usr/local/kafka/bin/kafka-server-start.sh ${KAFKA_CONFIG}/server.properties

SuccessExitStatus=0 143

Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```
Please pay additional attention on options:
```
 -Dcom.sun.management.jmxremote.port=<REPLACE_WITH_YOUR_JMX_PORT>
 -Dcom.sun.management.jmxremote.rmi.port=<REPLACE_WITH_YOUR_JMX_PORT>
```
To avoid using dynamic TCP port and firewall/NAT issues it is better to set static port setting.
## Restart kafka service
     systemctl daemon-reload
     systemctl restart kafka-service

# Zabbix configuration

#Upload scripts for discovery JMX

     git clone https://github.com/helli0n/kafka-monitoring.git 
     cd zabbix/kafka
     cp jmx_discovery /etc/zabbix/externalscripts
     cp JMXDiscovery-0.0.1.jar /etc/zabbix/externalscripts

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

For monitoring kafka consumers you should install [Burrow](https://github.com/linkedin/Burrow/) daemon and [jq](https://stedolan.github.io/jq/download/) tools on kafka host

***

# Kafka Consumer Monitoring

## Clone all stuff 
     ssh clone https://github.com/helli0n/kafka-monitoring.git
     cd kafka/kafkaconsumers
## Install burrow
     cp -r burrow /opt/
     cp burrow/ /etc/init.d/burrow_script
     chkconfig --level 345 burrow_script on
You should change config file in /opt/burrow/burrow.cfg
## Install jq 
     cd /usr/bin
     wget https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
     mv jq-linux64 jq
     chmod +x jq
## Check jq
     # jq 
     # jq 
     jq - commandline JSON processor [version 1.5]
     Usage: jq [options] <jq filter> [file...]
     jq is a tool for processing JSON inputs, applying the
     given filter to its JSON text inputs and producing the
     filter's results as JSON on standard output.
     The simplest filter is ., which is the identity filter,
     copying jq's input to its output unmodified (except for
     formatting).
     For more advanced filters see the jq(1) manpage ("man jq")
     and/or https://stedolan.github.io/jq
     Some of the options include:
     -c compact instead of pretty-printed output;
     -n use `null` as the single input value;
     -e set the exit status code based on the output;
     -s read (slurp) all inputs into an array; apply filter to it;
     -r output raw strings, not JSON texts;
     -R read raw strings, not JSON texts;
     -C colorize JSON;
     -M monochrome (don't colorize JSON);
     -S sort keys of objects on output;
     --tab use tabs for indentation;
     --arg a v set variable $a to value <v>;
     --argjson a v set variable $a to JSON value <v>;
     --slurpfile a f set variable $a to an array of JSON texts read from <f>;
     See the manpage for more options.
## Copy files to zabbix folder
     cp kafka_consumers.sh /etc/zabbix/
     cp userparameter_kafkaconsumer.conf /etc/zabbix/zabbix_agentd.d
     Start burrow and restart zabbix-agent
     /etc/init.d/burrow_script start
     /etc/init.d/zabbix-agent restart
Upload template [zbx_templates_kafkaconsumers.xml](https://github.com/helli0n/kafka-monitoring/blob/master/kafkaconsumers/zbx_templates_kafkaconsumers.xml) and mapping value [zbx_valuemaps_kafkaconsumers.xml](https://github.com/helli0n/kafka-monitoring/blob/master/kafkaconsumers/zbx_valuemaps_kafkaconsumers.xml) to zabbix server using UI and link template to Kafka host
# Troubleshooting 
If it doesn't work you can check it use **/etc/zabbix/kafka_consumers.sh**
e.g.:
      # /etc/zabbix/kafka_consumers.sh discovery
     {"data":[{
     "{#CONSUMER}": "CONSUMER0",
     "{#PARTITION}": 0,
     "{#TOPIC}": "TOPIC0"
     },{
     "{#CONSUMER}": "CONSUMER1",
     "{#PARTITION}": 0,
     "{#TOPIC}": "TOPIC1"
     }]}




# kafka-monitoring
http://adminotes.com/

https://github.com/helli0n/kafka-monitoring/wiki/Kafka-monitoring

https://engineering.linkedin.com/apache-kafka/burrow-kafka-consumer-monitoring-reinvented

https://github.com/linkedin/Burrow/wiki

https://community.hortonworks.com/articles/28103/monitoring-kafka-with-burrow.html
