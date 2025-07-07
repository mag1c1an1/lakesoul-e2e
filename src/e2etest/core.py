# SPDX-FileCopyrightText: LakeSoul Contributors
# 
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import shutil
from typing import Dict, List, Optional, override, Any
from pathlib import Path
import boto3
import click
import psycopg
import yaml
import logging
import requests

from pathlib import Path


VERSION = os.getenv("LAKESOUL_VERSION",None)
LAKESOUL_GIT = "https://github.com/lakesoul-io/LakeSoul.git"
TMP_CODE_DIR = Path("/tmp/lakesoul/e2e/code")
CONFIG_FILE = "config.yaml"
MVN_LOCAL = Path("~/.m2/repository/com/dmetasoul")

FLINK_VERSION = "1.20"
SPARK_VERSION = "3.3"

# lakesoul-flink
LAKESOUL_FLINK_PATH = Path(os.path.expanduser( f"{MVN_LOCAL}/lakesoul-flink/{FLINK_VERSION}-{VERSION}/lakesoul-flink-{FLINK_VERSION}-{VERSION}.jar"))
# lakesoul-spark
LAKESOUL_SPARK_PATH = Path(os.path.expanduser( f"{MVN_LOCAL}/lakesoul-spark/{SPARK_VERSION}-{VERSION}/lakesoul-spark-{SPARK_VERSION}-{VERSION}.jar"))
# lakesoul-pg
LAKESOUL_PG_URL = os.getenv("LAKESOUL_PG_URL",None)
LAKESOUL_PG_USER = os.getenv("LAKESOUL_PG_USER",None)
LAKESOUL_PG_PASSWORD = os.getenv("LAKESOUL_PG_PASSWORD",None)

# s3
END_POINT =  os.getenv("AWS_ENDPOINT",None)
ACCESS_KEY =os.getenv("AWS_SECRET_ACCESS_KEY",None) 
ACCESS_KEY_ID =os.getenv("AWS_ACCESS_KEY_ID",None) 
BUCKET = os.getenv("AWS_BUCKET",None)
S3_CLIENT= boto3.client(  
        's3',  
        aws_access_key_id=ACCESS_KEY_ID,  
        aws_secret_access_key=ACCESS_KEY,  
        endpoint_url=END_POINT
        )  

E2E_DATA_DIR = "lakesoul/e2e/data"
E2E_CLASSPATH ="m2"
E2E_CLASSPATH_WITH_ENDPOINT = f"{END_POINT}/{BUCKET}/{E2E_CLASSPATH}"



class SubTask:
    def run(self, **conf):
        pass

class CheckParquetSubTask(SubTask):
    def run(self, **conf):
        all_objects = s3_list_prefix(E2E_DATA_DIR)
        if len(all_objects) != 1:
            raise RuntimeError("data init failed")


class FlinkSubTask(SubTask):

    def __init__(self, name, entry, mode):
        self.name = name
        self.entry = entry
        self.mode = mode
        self.target = os.path.expanduser(
            f"{MVN_LOCAL}/flink-e2e/{VERSION}/flink-e2e-{VERSION}.jar"
        )

        self.lib = f"{END_POINT}/{BUCKET}/{E2E_CLASSPATH}/{LAKESOUL_FLINK_PATH.name}"

    def run(self, **conf):
        args = ["flink", "run", "--classpath", self.lib, "-c", self.entry, self.target]
        subprocess.run(args, check=True)

    def __repr__(self):
        return f"FlinkSubTask {{ {self.mode} {self.name} {self.entry} {self.target}}}"


class SparkSubTask(SubTask):

    def __init__(self, name, entry, mode):
        self.name = name
        self.entry = entry
        self.mode = mode
        self.target = os.path.expanduser(
            f"{MVN_LOCAL}/spark-e2e/{VERSION}/spark-e2e-{VERSION}.jar"
        )
        self.lib = f"s3://{BUCKET}/{E2E_CLASSPATH}/{LAKESOUL_SPARK_PATH.name}"

    def run(self, **conf):
        args = [
            "spark-submit",
            "--jars",
            self.lib, 
            "--class",
            self.entry,
            "--master",
            "local[*]",
            self.target,
        ]
        subprocess.run(args, check=True)

    def __repr__(self):
        return f"SparkSubTask {{ {self.mode} {self.name} {self.entry} {self.target}}}"


class Task:
    def __init__(self, sink: Optional[SubTask], source: Optional[SubTask]) -> None:
        self.sink = sink
        self.source = source

    def run(self):
        if self.sink:
            self.sink.run()
        if self.source:
            self.source.run()


class TaskRunner:
    def __init__(self, tasks: List[Task]) -> None:
        self.tasks = tasks

    def run(self):
        for t in self.tasks:
            t.run()


def clone_repo(repo_url:str, branch:str, dir:str) -> None:
    """clone repo from url

    Args:
        repo_url (str):  url used by git
        branch (str): which branch to clone
        dir (str): base dir of repo
    """
    logging.info(f"Cloning repository from {repo_url} (branch: {branch})...")
    origin = os.getcwd()
    os.chdir(dir)
    subprocess.run(
        ["git", "clone", "--depth=1", "--branch", branch, repo_url],
        check=True,
    )
    os.chdir(origin)
    logging.info("Repository cloned successfully.")


def build_install(base_dir: str):
    """build LakeSoul

    Args:
        dir (str): base dir of LakeSoul
    """
    origin = os.getcwd()
    os.chdir(base_dir)

    # build lakesoul itself
    subprocess.run(
        ["mvn", "clean", "install", "-DskipTests"],
        check=True,
    )
    # build e2eTests
    os.chdir("lakesoul-integ-test")
    subprocess.run(
        ["mvn", "clean", "install", "-DskipTests"],
        check=True,
    )
    os.chdir(origin)


def parse_subtask(conf: Dict[str, Any]) -> SubTask:
    logging.debug(conf)
    if conf["type"] == "flink":
        return FlinkSubTask(conf["name"], conf["entry"], conf["mode"])
    elif conf["type"] == "spark":
        return SparkSubTask(conf["name"], conf["entry"], conf["mode"])
    else:
        raise RuntimeError("Unsupported Engine")


def combine_subtasks(sinks: List[SubTask], source: List[SubTask]) -> List[Task]:

    res = []
    for sk in sinks:
        for se in source:
            res.append(Task(sk, se))

    return res


def parse_subtasks(conf: List[Dict[str, Any]]) -> List[SubTask]:
    print(conf)
    print(type(conf))
    res = []
    for t in conf:
        res.append(parse_subtask(t))
    return res


def parse_conf(conf: Dict[str, Any]) -> List[Task]:
    init_data_gen = parse_subtask(conf["init"])
    init_rename_data = CheckParquetSubTask()
    init_task = Task(init_data_gen, init_rename_data)

    sinks = parse_subtasks(conf["sinks"])
    sources = parse_subtasks(conf["sources"])

    tasks = [init_task] + combine_subtasks(sinks, sources)
    return tasks


# cli

@click.group()
@click.pass_context
@click.option(
    "-f",
    "--conf",
    default="config.yaml",
    type=click.Path(exists=True),
    help="config path",
)
@click.option("--fresh", is_flag=True, help="fresh clone lakesoul repo")
@click.option("--repo", default=LAKESOUL_GIT, help="LakeSoul repo")
@click.option(
    "--dir", default=TMP_CODE_DIR, type=click.Path(), help="dir of lakesoul code"
)
@click.option("-b", "--branch", default="main", help="lakesoul branch, default is main")
@click.option("--log", default="INFO", help="log level")
def cli(ctx, conf, fresh, repo, branch, dir, log):
    ctx.obj["conf"] = conf
    ctx.obj["fresh"] = fresh
    ctx.obj["branch"] = branch
    ctx.obj["dir"] = Path(dir)
    ctx.obj["repo"] = repo
    ctx.obj['log'] =log


def s3_upload_jars():
    """ upload installed lakesoul jars to s3
    """
    jars:List[Path] = [
        LAKESOUL_FLINK_PATH,
        LAKESOUL_SPARK_PATH
    ]

    for jar in jars:
        with open(jar,'rb') as data:
            S3_CLIENT.put_object(Bucket=BUCKET,Key=f"{E2E_CLASSPATH}/{jar.name}",Body=data,StorageClass='STANDARD')

def s3_delete_jars():
    """delete jars at s3
    """
    jars:List[Path] = [
        LAKESOUL_FLINK_PATH,
        LAKESOUL_SPARK_PATH
    ]
    for jar in jars:
        S3_CLIENT.delete_object(Bucket=BUCKET,Key=f"{E2E_CLASSPATH}/{jar.name}")
    
def s3_list_prefix(prefix: str):
    """list objects whicih has prefix

    Args:
        prefix (str): prefix of ths object
    """
    resp = S3_CLIENT.list_objects(Bucket=BUCKET,Prefix=prefix)
    objs = []
    try:

        for obj in resp['Contents']:
            objs.append({
                'Key':obj['Key']
            })
        return objs
    except KeyError:
        logging.info(f"[INFO] s3://{BUCKET}/{prefix} is empty")
        return []


def s3_delete_dir(dir:str):
    """delete a dir in s3 like local file system

    Args:
        dir (str): _description_
    """
    objs = s3_list_prefix(dir)
    if len(objs) != 0:
        S3_CLIENT.delete_objects(Bucket=BUCKET,Delete={'Objects':objs})

def init_log(loglevel:str):
    """init python logging

    Args:
        loglevel (str): log level

    Raises:
        ValueError: see source code
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)


def pre_run(ctx):
    if ctx.obj["fresh"]:
        # remove dir
        if ctx.obj["dir"].exists():
            shutil.rmtree(ctx.obj["dir"])  # 如果临时目录已存在，先删除
        os.makedirs(ctx.obj["dir"])
        # clone_repo(ctx.obj["repo"], ctx.obj["branch"], ctx.obj["dir"])

    s3_delete_dir(E2E_DATA_DIR)
        
    with open(ctx.obj["conf"]) as f:
        ctx.obj["config"] = yaml.safe_load(f)

    # build lakesoul
    # build_install(ctx.obj["dir"] / "LakeSoul")
    s3_upload_jars()


@click.command()
@click.pass_context
def run(ctx):
    init_log(ctx.obj['log'])
    pre_run(ctx)
    tasks = parse_conf(ctx.obj["config"])
    runner = TaskRunner(tasks)
    runner.run()


def check_pg():
    try:
        if LAKESOUL_PG_URL is None or LAKESOUL_PG_USER is None or LAKESOUL_PG_PASSWORD is None:
            raise ValueError("some of env variables [`LAKESOUL_PG_URL`,`LAKESOUL_PG_USER`,`LAKESOUL_PG_PASSWORD`] are not set")
        pg_url = LAKESOUL_PG_URL[5:LAKESOUL_PG_URL.find('?')]
        conn = psycopg.connect(conninfo=pg_url,user = LAKESOUL_PG_USER, password = LAKESOUL_PG_PASSWORD)
        conn.close()
        logging.info("check pg success")
    except Exception as e:
        logging.error(f"connect pg failed by {e}")
    

def check_minio():
    try:
        if END_POINT is None or ACCESS_KEY is None or ACCESS_KEY_ID is None:
            raise ValueError("some of env variables [`AWS_ENDPOINT`,`AWS_SECRET_ACCESS_KEY`,`AWS_ACCESS_KEY_ID`] are not set")
        response = requests.get(f"{END_POINT}/minio/health/live")
        if response.status_code == 200:
            logging.info("check minio service success")
        else:
            logging.warning(f"MinIO 服务异常，状态码: {response.status_code}")
    except Exception as e:
        logging.error(f"check minio service failed by {e}")

def check_clients():
    try:
        subprocess.run(['flink','--version'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['spark-submit','--version'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        logging.info(f"check clients success")
    except Exception as e:
        logging.error(f"check clients failed by {e}")

@click.command()
@click.pass_context
def check(ctx):
    init_log(ctx.obj['log'])
    check_pg()
    check_minio()
    check_clients()