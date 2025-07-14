set dotenv-load


env := "AWS_SECRET_ACCESS_KEY=minioadmin1 \
AWS_ACCESS_KEY_ID=minioadmin1  \
AWS_ENDPOINT=http://localhost:9000  \
AWS_BUCKET=lakesoul-test-bucket  \
LAKESOUL_VERSION=3.0.0-SNAPSHOT  \
LAKESOUL_PG_URL=jdbc:postgresql://127.0.0.1:5432/lakesoul_test?stringtype=unspecified \
LAKESOUL_PG_USERNAME=lakesoul_test \
LAKESOUL_PG_PASSWORD=lakesoul_test"

k8s-env := "AWS_SECRET_ACCESS_KEY=minioadmin1 \
AWS_ACCESS_KEY_ID=minioadmin1  \
AWS_ENDPOINT=http://miniosvc.lakesoul-basic-env.svc.cluster.local:9000  \
AWS_BUCKET=lakesoul-test-bucket  \
LAKESOUL_VERSION=3.0.0-SNAPSHOT  \
LAKESOUL_PG_URL=jdbc:postgresql://pgsvc.lakesoul-basic-env.svc.cluster.local:5432/lakesoul_test?stringtype=unspecified \
LAKESOUL_PG_USERNAME=lakesoul_test \
LAKESOUL_PG_PASSWORD=lakesoul_test"

env:
    {{k8s-env}}

pytest:
     {{env}} uv run pytest

check: 
    {{env}} uv run e2etest check

build:
    uv build

run:
    {{env}} e2etest --repo https://github.com/mag1c1an1/Lakesoul.git --branch tmp_name run

image-e2e version:
    docker build -t dmetasoul-repo/e2e:{{version}} -f lakesoul-e2e.Dockerfile .

tag version:
    docker tag dmetasoul-repo/e2e:{{version}} swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/e2e:{{version}}

push version:
    docker push swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/e2e:{{version}}

pods:
    kubectl -n lakesoul-basic-env get pods

reset:
    -kubectl delete ns lakesoul-basic-env
    kubectl create ns lakesoul-basic-env

e2e-run version:
    docker run -it --rm -v $HOME/.kube:/root/.kube -v $FLINK_HOME/conf/config.yaml:/opt/flink-1.20.1/conf/config.yaml dmetasoul-repo/e2e:{{version}} /bin/bash

upload:
    mcli cp ~/.m2/repository/com/dmetasoul/flink-e2e/3.0.0-SNAPSHOT/flink-e2e-3.0.0-SNAPSHOT.jar hwoss/dmetasoul-bucket/jiax/target/flink-e2e-3.0.0-SNAPSHOT.jar
    mcli cp ~/.m2/repository/com/dmetasoul/lakesoul-flink/1.20-3.0.0-SNAPSHOT/lakesoul-flink-1.20-3.0.0-SNAPSHOT.jar hwoss/dmetasoul-bucket/jiax/target/lakesoul-flink-1.20-3.0.0-SNAPSHOT.jar
    mcli cp ~/.m2/repository/com/dmetasoul/lakesoul-spark/3.3-3.0.0-SNAPSHOT/lakesoul-spark-3.3-3.0.0-SNAPSHOT.jar hwoss/dmetasoul-bucket/jiax/target/lakesoul-spark-3.3-3.0.0-SNAPSHOT.jar

rm:
    mcli rm  hwoss/dmetasoul-bucket/jiax/target/flink-e2e-3.0.0-SNAPSHOT.jar
    mcli rm  hwoss/dmetasoul-bucket/jiax/target/lakesoul-flink-1.20-3.0.0-SNAPSHOT.jar
    mcli rm  hwoss/dmetasoul-bucket/jiax/target/lakesoul-spark-3.3-3.0.0-SNAPSHOT.jar

debug:
    flink run-application --target kubernetes-application \
    --class com.dmetasoul.e2e.FlinkDataSink \
    -Dcontainerized.master.env.LAKESOUL_PG_DRIVER=com.lakesoul.shaded.org.postgresql.Driver \
    -Dcontainerized.master.env.LAKESOUL_PG_USERNAME=lakesoul_e2e \
    -Dcontainerized.master.env.LAKESOUL_PG_PASSWORD=lakesoul_e2e \
    -Dcontainerized.master.env.LAKESOUL_PG_URL=jdbc:postgresql://pgsvc.default.svc.cluster.local:5432/lakesoul_e2e?stringtype=unspecified \
    -Dcontainerized.taskmanager.env.LAKESOUL_PG_DRIVER=com.lakesoul.shaded.org.postgresql.Driver \
    -Dcontainerized.taskmanager.env.LAKESOUL_PG_USERNAME=lakesoul_e2e \
    -Dcontainerized.taskmanager.env.LAKESOUL_PG_PASSWORD=lakesoul_e2e \
    -Dcontainerized.taskmanager.env.LAKESOUL_PG_URL=jdbc:postgresql://pgsvc.default.svc.cluster.local:5432/lakesoul_e2e?stringtype=unspecified \
    -Dkubernetes.artifacts.local-upload-enabled=true \
    -Dkubernetes.artifacts.local-upload-overwrite=true \
    -Dkubernetes.artifacts.local-upload-target=s3://dmetasoul-bucket/jiax/target/ \
    -Dkubernetes.cluster-id=lakesoul-e2e-flink \
    -Dkubernetes.container.image.ref=swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/flink-hadoop-3.3.6:1.0 \
    -Duser.artifacts.artifact-list=s3://dmetasoul-bucket/jiax/target/lakesoul-flink-1.20-3.0.0-SNAPSHOT.jar \
    s3://dmetasoul-bucket/jiax/target/flink-e2e-3.0.0-SNAPSHOT.jar

del:
    kubectl delete deployment lakesoul-e2e-flink

# build_with_hadoop version:
# pass