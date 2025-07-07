env := "AWS_SECRET_ACCESS_KEY=minioadmin1 \
AWS_SECRET_KEY_ID=minioadmin1  \
AWS_ENDPOINT=http://localhost:9000  \
AWS_BUCKET=lakesoul-test-bucket  \
LAKESOUL_VERSION=3.0.0-SNAPSHOT  \
LAKESOUL_PG_URL=jdbc:postgresql://127.0.0.1:5432/lakesoul_test?stringtype=unspecified \
LAKESOUL_PG_USER=lakesoul_test \
LAKESOUL_PG_PASSWORD=lakesoul_test"

pytest:
     {{env}} uv run pytest

check: 
    {{env}} uv run e2etest check

build:
    uv build

debug:
    python3 ./main.py --dir /Users/mag1cian/dev/internship run

test:
    {{env}} uv run main.py --fresh --repo https://github.com/mag1c1an1/LakeSoul.git --branch tmp_name run  

help:
    python3 ./main.py --help

image-archlinux:
    docker tag docker.1ms.run/archlinux/archlinux:base-devel-20250630.0.373922 dmetasoul/archlinux:v1

image-base version:
    docker build -t dmetasoul/dev-base:{{version}} -f dev-base.Dockerfile  .

image-all version: (image-base version)
    docker build -t dmetasoul/dev-all:{{version}} -f dev-all.Dockerfile .

image-e2e version: (image-all version)
    docker build -t dmetasoul/e2e:{{version}} -f lakesoul-e2e.Dockerfile .

pods:
    kubectl -n lakesoul-basic-env get pods

apply-basic:
    kubectl -n lakesoul-basic-env apply -f lakesoul_basic.yaml




