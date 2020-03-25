from rethinkdb import r

DB = "healthchecker"
REPORTS = "reports"
TARGETS = "targets"


def db():
    return r.db(DB)


def t_reports():
    return db().table(REPORTS)


def t_targets():
    return db().table(TARGETS)


def connect():
    conn = r.connect("db")
    queries = [
        r.db_create(DB),
        db().table_create(REPORTS),
        db().table_create(TARGETS),
        t_reports().index_create("target_id"),
        t_reports().index_create("date"),
    ]
    for q in queries:
        try:
            q.run(conn)
        except r.RqlRuntimeError:
            pass
    return conn
