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

image-archlinux:
    docker tag docker.1ms.run/archlinux/archlinux:base-devel-20250630.0.373922 dmetasoul/archlinux:v1

image-base version:
    docker build -t dmetasoul-repo/dev-base:{{version}} -f dev-base.Dockerfile  .

image-all version: (image-base version)
    docker build -t dmetasoul-repo/dev-all:{{version}} -f dev-all.Dockerfile .

image-e2e version: (image-all version)
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
    docker run -v $HOME/.kube:/root/.kube -v $FLINK_HOME/conf/config.yaml:/opt/flink-1.20.1/conf/config.yaml swr.cn-southwest-2.myhuaweicloud.com/dmetasoul-repo/e2e:{{version}} /bin/bash

