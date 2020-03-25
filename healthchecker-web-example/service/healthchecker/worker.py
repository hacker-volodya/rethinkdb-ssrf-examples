import os
from datetime import timedelta
from healthchecker.db import t_targets, connect, t_reports
from rethinkdb import r

from celery import Celery

period = timedelta(minutes=1)
broker_dir = "/tmp"

for f in ["out", "processed"]:
    if not os.path.exists(os.path.join(broker_dir, f)):
        os.makedirs(os.path.join(broker_dir, f))


app = Celery(__name__)
app.conf.update(
    {
        "broker_url": "filesystem://",
        "broker_transport_options": {
            "data_folder_in": os.path.join(broker_dir, "out"),
            "data_folder_out": os.path.join(broker_dir, "out"),
            "data_folder_processed": os.path.join(broker_dir, "processed"),
        },
        "result_persistent": False,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
    }
)

app.conf.beat_schedule = {
    "check_targets": {
        "task": "check_targets",
        "schedule": period,
        "options": {"expires": period.total_seconds()},
    }
}


@app.task(bind=True, name="check_targets")
def check_targets(self):
    conn = connect()
    for target in t_targets().run(conn):
        kwargs = {
            "attempts": 1,
            "timeout": period.total_seconds(),
            "result_format": "binary",
            "method": target["method"],
        }
        if kwargs["method"] == "POST":
            kwargs["data"] = target["body"]

        add_report_query = lambda msg: t_reports().insert(
            {"target_id": target["id"], "date": r.now(), "message": msg}
        )
        http_query = r.http(target["url"], **kwargs).default(lambda x: x)
        add_report_query(http_query).run(conn)
    conn.close()
