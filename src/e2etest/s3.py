from pathlib import Path
from typing import List
import logging

from e2etest.vars import (
    BUCKET,
    E2E_CLASSPATH,
    LAKESOUL_FLINK_PATH,
    LAKESOUL_SPARK_PATH,
    S3_CLIENT,
)


def s3_upload_jars():
    """upload installed lakesoul jars to s3"""
    jars: List[Path] = [LAKESOUL_FLINK_PATH, LAKESOUL_SPARK_PATH]

    for jar in jars:
        with open(jar, "rb") as data:
            S3_CLIENT.put_object(
                Bucket=BUCKET,
                Key=f"{E2E_CLASSPATH}/{jar.name}",
                Body=data,
                StorageClass="STANDARD",
            )


def s3_delete_jars():
    """delete jars at s3"""
    jars: List[Path] = [LAKESOUL_FLINK_PATH, LAKESOUL_SPARK_PATH]
    for jar in jars:
        S3_CLIENT.delete_object(Bucket=BUCKET, Key=f"{E2E_CLASSPATH}/{jar.name}")


def s3_list_prefix(prefix: str):
    """list objects whicih has prefix

    Args:
        prefix (str): prefix of ths object
    """
    resp = S3_CLIENT.list_objects(Bucket=BUCKET, Prefix=prefix)
    objs = []
    try:
        for obj in resp["Contents"]:
            objs.append({"Key": obj["Key"]})
        return objs
    except KeyError:
        logging.info(f"[INFO] s3://{BUCKET}/{prefix} is empty")
        return []


def s3_delete_dir(dir: str):
    """delete a dir in s3 like local file system

    Args:
        dir (str): _description_
    """
    objs = s3_list_prefix(dir)
    if len(objs) != 0:
        S3_CLIENT.delete_objects(Bucket=BUCKET, Delete={"Objects": objs})
