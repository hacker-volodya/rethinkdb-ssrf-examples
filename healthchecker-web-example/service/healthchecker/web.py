from flask import Flask, render_template, request, redirect
from healthchecker.db import connect, t_reports, t_targets
from rethinkdb import r

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    conn = connect()
    if request.method == "POST":
        url = request.form["url"]
        method = request.form["method"]
        body = request.form["body"]
        assert method in ["POST", "GET"]
        target = {"url": url, "method": method, "body": body}
        t_targets().insert(target).run(conn)

    targets = list(
        t_targets()
        .merge(
            lambda t: {
                "reports": t_reports()
                .get_all(t["id"], index="target_id")
                .order_by(r.desc("date"))
                .limit(5)
                .coerce_to("array")
            }
        )
        .run(conn)
    )
    conn.close()
    return render_template("index.html", targets=targets)


@app.route("/delete/<target_id>", methods=["POST"])
def delete(target_id):
    conn = connect()
    t_targets().get(target_id).delete().run(conn)
    t_reports().filter(lambda x: x["target_id"] == target_id).delete().run(conn)
    conn.close()
    return redirect("/")
