# SPDX-FileCopyrightText: LakeSoul Contributors
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import shutil
from typing import Dict, List, Any
from pathlib import Path
import click
import yaml
import logging

from e2etest.checks import check_clients, check_minio, check_pg
from e2etest.s3 import s3_delete_dir, s3_upload_jars
from e2etest.task import (
    CheckParquetSubTask,
    FlinkSubTask,
    SparkSubTask,
    SubTask,
    Task,
    TaskRunner,
)
from e2etest.vars import E2E_DATA_DIR, LAKESOUL_GIT, TMP_CODE_DIR


def clone_repo(repo_url: str, branch: str, dir: str) -> None:
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


def parse_subtask(
    conf: Dict[str, Any], spark_deploy: Dict[str, str], flink_conf: Dict[str, str]
) -> SubTask:
    logging.debug(conf)
    if conf["type"] == "flink":
        return FlinkSubTask(conf["name"], conf["entry"], conf["mode"], flink_conf)
    elif conf["type"] == "spark":
        return SparkSubTask(conf["name"], conf["entry"], conf["mode"], spark_deploy)
    else:
        raise RuntimeError("Unsupported Engine")


def combine_subtasks(sinks: List[SubTask], source: List[SubTask]) -> List[Task]:
    """Make sink - source pairs

    Args:
        sinks (List[SubTask]): sink subtasks (write to lakesoul)
        source (List[SubTask]): source subtasks (read from lakesoul)

    Returns:
        List[Task]: tasks
    """
    res = []
    for sk in sinks:
        for se in source:
            res.append(Task(sk, se))

    return res


def parse_subtasks(
    conf: List[Dict[str, Any]], spark_conf: Dict[str, str], flink_conf: Dict[str, str]
) -> List[SubTask]:
    print(conf)
    print(type(conf))
    res = []
    for t in conf:
        res.append(parse_subtask(t, spark_conf, flink_conf))
    return res


def parse_conf(conf: Dict[str, Any]) -> List[Task]:
    """Parse configration to actually tasks

    Args:
        conf (Dict[str, Any]): config dict

    Returns:
        List[Task]: list of task
    """
    spark_conf = conf["spark"]
    flink_conf = conf["flink"]

    init_data_gen = parse_subtask(conf["init"], spark_conf, flink_conf)
    init_rename_data = CheckParquetSubTask()
    init_task = Task(init_data_gen, init_rename_data)

    sinks = parse_subtasks(conf["sinks"], spark_conf, flink_conf)
    sources = parse_subtasks(conf["sources"], spark_conf, flink_conf)

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
    ctx.obj["log"] = log


def init_log(loglevel: str):
    """init python logging

    Args:
        loglevel (str): log level

    Raises:
        ValueError: see source code
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)


def pre_run(ctx):
    """Execute preparation tasks

    Args:
        ctx: cli parameters
    """
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
    init_log(ctx.obj["log"])
    pre_run(ctx)
    tasks = parse_conf(ctx.obj["config"])
    runner = TaskRunner(tasks)
    runner.run()


@click.command()
@click.pass_context
def check(ctx):
    init_log(ctx.obj["log"])
    check_pg()
    check_minio()
    check_clients()
