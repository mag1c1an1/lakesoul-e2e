# SPDX-FileCopyrightText: LakeSoul Contributors
#
# SPDX-License-Identifier: Apache-2.0

"""
Global Variable definition
"""

import os
from pathlib import Path
import boto3

VERSION = os.getenv("LAKESOUL_VERSION", None)
LAKESOUL_GIT = "https://github.com/lakesoul-io/LakeSoul.git"
TMP_CODE_DIR = Path("/tmp/lakesoul/e2e/code")
CONFIG_FILE = "config.yaml"
MVN_LOCAL = Path("~/.m2/repository/com/dmetasoul")

FLINK_VERSION = "1.20"
SPARK_VERSION = "3.3"

# lakesoul-flink
LAKESOUL_FLINK_PATH = Path(
    os.path.expanduser(
        f"{MVN_LOCAL}/lakesoul-flink/{FLINK_VERSION}-{VERSION}/lakesoul-flink-{FLINK_VERSION}-{VERSION}.jar"
    )
)
# lakesoul-spark
LAKESOUL_SPARK_PATH = Path(
    os.path.expanduser(
        f"{MVN_LOCAL}/lakesoul-spark/{SPARK_VERSION}-{VERSION}/lakesoul-spark-{SPARK_VERSION}-{VERSION}.jar"
    )
)
# lakesoul-pg
LAKESOUL_PG_URL = os.getenv("LAKESOUL_PG_URL", None)
LAKESOUL_PG_USERNAME = os.getenv("LAKESOUL_PG_USERNAME", None)
LAKESOUL_PG_PASSWORD = os.getenv("LAKESOUL_PG_PASSWORD", None)

# s3
END_POINT = os.getenv("AWS_ENDPOINT", None)
ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
BUCKET = os.getenv("AWS_BUCKET", None)
S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_KEY,
    endpoint_url=END_POINT,
)

E2E_DATA_DIR = "lakesoul/e2e/data"
E2E_CLASSPATH = "m2"
E2E_CLASSPATH_WITH_ENDPOINT = f"{END_POINT}/{BUCKET}/{E2E_CLASSPATH}"
