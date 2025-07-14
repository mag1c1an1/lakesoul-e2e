FROM swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/flink:1.20.1-scala_2.12-java11
RUN mkdir -p /opt/flink/plugins/s3
RUN cp /opt/flink/opt/flink-s3-fs-hadoop-1.20.1.jar /opt/flink/plugins/s3/
COPY opt/hadoop-3.3.6.tar.gz /opt/flink/hadoop-3.3.6.tar.gz
RUN tar -xzf /opt/flink/hadoop-3.3.6.tar.gz
ENV HADOOP_CLASSPATH=/opt/flink/hadoop-3.3.6/etc/hadoop:/opt/flink/hadoop-3.3.6/share/hadoop/common/lib/*:/opt/flink/hadoop-3.3.6/share/hadoop/common/*:/opt/flink/hadoop-3.3.6/share/hadoop/hdfs:/opt/flink/hadoop-3.3.6/share/hadoop/hdfs/lib/*:/opt/flink/hadoop-3.3.6/share/hadoop/hdfs/*:/opt/flink/hadoop-3.3.6/share/hadoop/mapreduce/*:/opt/flink/hadoop-3.3.6/share/hadoop/yarn:/opt/flink/hadoop-3.3.6/share/hadoop/yarn/lib/*:/opt/flink/hadoop-3.3.6/share/hadoop/yarn/*
COPY opt/parquet-hadoop-bundle-1.13.1.jar /opt/flink/lib/