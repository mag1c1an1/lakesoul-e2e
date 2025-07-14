application mode

# PG

docker run -d --name lakesoul-e2e-pg -p4321:5432 -e POSTGRES_USER=lakesoul_e2e -e POSTGRES_PASSWORD=lakesoul_e2e -e POSTGRES_DB=lakesoul_e2e -d swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/postgres:14.5 

docker cp meta_init.sql lakesoul-e2e-pg:/ 

docker exec -i lakesoul-e2e-pg sh -c "PGPASSWORD=lakesoul_e2e psql -h localhost -p 5432 -U lakesoul_e2e -f meta_init.sql"

# important
pipx install is slow

# K8S

## flink 

flink run-application --target kubernetes-application \
--class com.dmetasoul.FlinkDataInit \
-Dkubernetes.cluster-id=lakesoul-e2etest \
-Dkubernetes.container.image.ref=swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/flink:1.20.1-scala_2.12-java11 \
-Dcontainerized.master.env.ENABLE_BUILT_IN_PLUGINS=flink-s3-fs-hadoop-1.20.1.jar \
-Dcontainerized.taskmanager.env.ENABLE_BUILT_IN_PLUGINS=flink-s3-fs-hadoop-1.20.1.jar \
-Duser.artifacts.artifact-list=s3://dmetasoul-bucket/jiax/target/lakesoul-flink.jar \
s3://dmetasoul-bucket/jiax/target/first-love-0.1.jar