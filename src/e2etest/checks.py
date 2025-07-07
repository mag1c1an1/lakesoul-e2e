"""
check e2e test environment settings mainly for k8s . Ex: postgresql, minio and compute engines.
"""

import logging
import subprocess
import psycopg
import requests
from e2etest.vars import (
    ACCESS_KEY,
    ACCESS_KEY_ID,
    END_POINT,
    LAKESOUL_PG_PASSWORD,
    LAKESOUL_PG_URL,
    LAKESOUL_PG_USERNAME,
)


def check_pg():
    try:
        if (
            LAKESOUL_PG_URL is None
            or LAKESOUL_PG_USERNAME is None
            or LAKESOUL_PG_PASSWORD is None
        ):
            raise ValueError(
                "some of env variables [`LAKESOUL_PG_URL`,`LAKESOUL_PG_USER`,`LAKESOUL_PG_PASSWORD`] are not set"
            )
        pg_url = LAKESOUL_PG_URL[5 : LAKESOUL_PG_URL.find("?")]
        conn = psycopg.connect(
            conninfo=pg_url, user=LAKESOUL_PG_USERNAME, password=LAKESOUL_PG_PASSWORD
        )
        conn.close()
        logging.info("check pg success")
    except Exception as e:
        logging.error(f"connect pg failed by {e}")


def check_minio():
    try:
        if END_POINT is None or ACCESS_KEY is None or ACCESS_KEY_ID is None:
            raise ValueError(
                "some of env variables [`AWS_ENDPOINT`,`AWS_SECRET_ACCESS_KEY`,`AWS_ACCESS_KEY_ID`] are not set"
            )
        response = requests.get(f"{END_POINT}/minio/health/live")
        if response.status_code == 200:
            logging.info("check minio service success")
        else:
            logging.warning(f"MinIO 服务异常，状态码: {response.status_code}")
    except Exception as e:
        logging.error(f"check minio service failed by {e}")


def check_clients():
    try:
        subprocess.run(
            ["flink", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["spark-submit", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info("check clients success")
    except Exception as e:
        logging.error(f"check clients failed by {e}")
