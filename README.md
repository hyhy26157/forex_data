# forex_data

using kafka to take in forex data from finnhub API and 


#Using GCP VM
1. install gcp
https://cloud.google.com/sdk/docs/install
2. get a cloud account and create cloud vm (using gcp here)
https://cloud.google.com/compute/docs/instances/create-start-instance
Using ubuntu image
3. connect to gcp vm
gcloud init
gcloud compute ssh <VM name> --zone= <Zone Name>
note: If you have a dynamic IP address like mine, remember to check your IP address before login and put it on the VM firewall whitelist.
4. Update and Install Java JDK version 8+
Optional: sudo adduser <newuser>
sudo apt-get update
sudo apt-get install openjdk-8-jdk
java -version
5. Download & unzip Apache Zookeeper
wget https://dlcdn.apache.org/zookeeper/zookeeper-3.8.1/apache-zookeeper-3.8.1-bin.tar.gz
tar -xsf <zookeeper-3.8.1-bin.tar.gz>
6. Download & unzip Apache Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
tar -xsf <kafka-3.5.0-bin.tar.gz>

7. Download & unzip Spark
wget <spark download link>
# install spark-kafka dependencies
spark-shell --packages org.apache.spark:spark-sql-kafka-0-10_2.12:< spark downloaded version >

8. Configuration of spark and kafka
# define spark environment in .bashrc
export SPARK_HOME=/home/<username>/where/your/spark/file/is/
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
source .bashrc 

# start spark
$SPARK_HOME/sbin/start-master.sh
# find the start master location
/opt/spark/spark-3.4.0-binhadoop3/logs/<*.Master-1-hdfs>.out
look something like this spark://spark.asia-southeast1-b.c.banded-nimbus-393607.internal:7077
# run slave (single server setup)
$SPARK_HOME/sbin/start-worker.sh spark://spark.asia-southeast1-b.c.banded-nimbus-393607.internal:7077



# setup zookeeper systemmd
sudo nano /etc/systemd/system/zookeeper.service

[Unit]
Description=Apache Zookeeper server
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target
[Service]
Type=simple
ExecStart=/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties
ExecStop=/usr/local/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal
[Install]
WantedBy=multi-user.target

# setup kafka systemmd
sudo gedit /etc/systemd/system/kafka.service

[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
Requires=zookeeper.service
[Service]
Type=simple
Environment="JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64"
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh
[Install]
WantedBy=multi-user.target

9. data ingestion

order of operations matters here. 
start Zookeeper --> start Kafka --> create topic --> start producer --> producing data from producer --> start consumer

# start zookeeper, then kafka
sudo systemctl daemon-reload
sudo systemctl start zookeeper
sudo systemctl start kafka

<optional>
systemctl status
sudo systemctl status zookeeper
sudo systemctl status kafka
Note: clear your tmp/kafka-logs if kafka fail to start.

# create a pyscript to connect with a data source (creating a data source)
see finnhub.py
Note: only data in producer.send() will the consumer receive. everything is is just output print which consumer cannot listen.

# create kafka producer take in the pyscript (start topic)
/home/usr/to/kafka/folder/bin/kafka-topics.sh --create --topic forex_producer --bootstrap-server <internal IP address>:9092 --partitions 1 --replication-factor 1

# check if topic is running
/home/usr/to/kafka/folder/bin/kafka-topics.sh --list --bootstrap-server <internal IP address>:9092
# delete topic
/home/usr/to/kafka/folder/bin/kafka-topics.sh --bootstrap-server <internal IP address>:9092 --delete --topic <topic name>

# get finnhub.py to VM

# run pyscript file (start producer, producing data from producer)
python3 /home/usr/folder/to/your/python/file/finnhub.py

# create a kafka consumer to listen to the producer and shout out the data (start consumer)
bin/kafka-console-consumer.sh --topic finnhub --bootstrap-server <internal IP address>:9092                           

#testing between producer and consumer <optional>
bin/kafka-console-consumer.sh --bootstrap-server 10.148.0.8:9092 --topic forex --from-beginning

10. data transformation
# run spark structured streaming /see step 7, to specify the dependency (kafka in this case), to run when running spark stream
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:<spark downloaded version> ~/forex_data/sparkstreaming.py
