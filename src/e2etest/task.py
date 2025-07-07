import os
import subprocess
from typing import List, Optional
from e2etest.s3 import s3_list_prefix
from e2etest.vars import (
    BUCKET,
    E2E_CLASSPATH,
    E2E_DATA_DIR,
    END_POINT,
    LAKESOUL_FLINK_PATH,
    LAKESOUL_SPARK_PATH,
    MVN_LOCAL,
    VERSION,
)


class SubTask:
    """Subprocess Wrapper"""

    def run(self, **conf):
        pass


class CheckParquetSubTask(SubTask):
    """Check whether the data file is generated successfully"""

    def run(self, **conf):
        all_objects = s3_list_prefix(E2E_DATA_DIR)
        if len(all_objects) != 1:
            raise RuntimeError("data init failed")


class FlinkSubTask(SubTask):
    """Act as a flink task"""

    def __init__(self, name, entry, mode, conf):
        self.name = name
        self.entry = entry
        self.mode = mode
        self.depoly = conf["deploy"]
        self.jobmanager = conf["jobmanager"]
        self.target = os.path.expanduser(
            f"{MVN_LOCAL}/flink-e2e/{VERSION}/flink-e2e-{VERSION}.jar"
        )

        self.lib = f"{END_POINT}/{BUCKET}/{E2E_CLASSPATH}/{LAKESOUL_FLINK_PATH.name}"

    def run(self, **conf):
        args = ["flink", "run", "--classpath", self.lib, "-c", self.entry, self.target]
        if self.depoly == "k8s":
            manager_args = ["-m", self.jobmanager]
            args[2:2] = manager_args
        subprocess.run(args, check=True)

    def __repr__(self):
        return f"FlinkSubTask {{ {self.mode} {self.name} {self.entry} {self.target} {self.depoly} {self.jobmanager}}}"


class SparkSubTask(SubTask):
    """Act as a spark task"""

    def __init__(self, name, entry, mode, conf):
        self.name = name
        self.entry = entry
        self.mode = mode
        self.deploy = conf["deploy"]
        self.target = os.path.expanduser(
            f"{MVN_LOCAL}/spark-e2e/{VERSION}/spark-e2e-{VERSION}.jar"
        )
        self.lib = f"s3://{BUCKET}/{E2E_CLASSPATH}/{LAKESOUL_SPARK_PATH.name}"

    def run(self, **conf):
        # todo
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
    """Task combine a sink task with a source task"""

    def __init__(self, sink: Optional[SubTask], source: Optional[SubTask]) -> None:
        self.sink = sink
        self.source = source

    def run(self):
        if self.sink:
            self.sink.run()
        if self.source:
            self.source.run()


class TaskRunner:
    """Run tasks in queue"""

    def __init__(self, tasks: List[Task]) -> None:
        self.tasks = tasks

    def run(self):
        for t in self.tasks:
            t.run()
