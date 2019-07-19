import glob
from dataclasses import dataclass
from datetime import datetime
from operator import attrgetter
from os import path

from dramatiq.message import Message


@dataclass
class Queue:
    name: str
    jobs: int
    jobs_delayed: int
    jobs_dead: int


@dataclass
class Worker:
    name: str
    last_seen: datetime
    jobs_in_flight: int


@dataclass
class Job:
    message_id: str
    message: Message
    eta: datetime
    timestamp: datetime
    retries: int

    @classmethod
    def from_message(cls, message):
        return cls(
            message_id=message.options.get("redis_message_id", message.message_id),
            message=message,
            eta=datetime.utcfromtimestamp(message.options.get("eta", message.message_timestamp) / 1000),
            timestamp=datetime.utcfromtimestamp(message.message_timestamp / 1000),
            retries=message.options.get("retries", 0),
        )

    def __repr__(self):
        return repr(self.message)

    def __str__(self):
        return str(self.message)

    def __getattr__(self, name):
        return getattr(self.message, name)


class RedisInterface:
    def __init__(self, broker):
        self.broker = broker
        self.scripts = {name: broker.client.register_script(script) for name, script in _scripts.items()}

    def qualify(self, key):
        return f"{self.broker.namespace}:{key}"

    @property
    def queues(self):
        queues = []
        for name, jobs, jobs_delayed, jobs_dead in self.do_get_queues_stats(*self.broker.queues):
            queues.append(Queue(
                name=name.decode("utf-8"),
                jobs=jobs,
                jobs_delayed=jobs_delayed,
                jobs_dead=jobs_dead,
            ))

        return sorted(queues, key=attrgetter("name"))

    @property
    def workers(self):
        workers = []
        for name, timestamp, jobs_in_flight in self.do_get_workers():
            workers.append(Worker(
                name=name.decode("utf-8"),
                last_seen=datetime.utcfromtimestamp(int(timestamp.decode("utf-8")) / 1000),
                jobs_in_flight=jobs_in_flight,
            ))

        return sorted(workers, key=attrgetter("name"))

    def get_queue(self, queue_name):
        for name, jobs, jobs_delayed, jobs_dead in self.do_get_queues_stats(queue_name):
            return Queue(
                name=name.decode("utf-8"),
                jobs=jobs,
                jobs_delayed=jobs_delayed,
                jobs_dead=jobs_dead,
            )

    def get_jobs(self, queue_name, cursor=0):
        next_cursor, messages_data = self.broker.client.hscan(
            self.qualify(f"{queue_name}.msgs"), cursor, count=300,
        )

        if next_cursor == cursor:
            next_cursor = None

        jobs = [Job.from_message(Message.decode(data)) for data in messages_data.values()]
        return next_cursor, sorted(jobs, key=attrgetter("timestamp"), reverse=True)

    def get_job(self, queue_name, message_id):
        data = self.broker.client.hget(self.qualify(f"{queue_name}.msgs"), message_id)
        return data and Job.from_message(Message.decode(data))

    def delete_message(self, queue_name, message_id):
        self.do_delete_message(queue_name, message_id)

    def _dispatch(self, command):
        dispatch = self.scripts["dispatch"]
        keys = [self.broker.namespace]

        def do_dispatch(*args):
            return dispatch(args=[command, *args], keys=keys)
        return do_dispatch

    def __getattr__(self, name):
        if not name.startswith("do_"):
            raise AttributeError(f"attribute {name} does not exist")

        command = name[len("do_"):]
        return self._dispatch(command)


_scripts = {}
_scripts_path = path.join(path.abspath(path.dirname(__file__)), "redis")
for filename in glob.glob(path.join(_scripts_path, "*.lua")):
    script_name, _ = path.splitext(path.basename(filename))
    with open(filename, "rb") as f:
        _scripts[script_name] = f.read()
