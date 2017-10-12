import binascii
import argparse
from datetime import datetime
import json
import os
import sqlite3


QUERY = (
    'SELECT pushes.time, head_changeset FROM trees, pushes, changeset_pushes '
    'WHERE pushes.push_id = changeset_pushes.push_id AND '
    'pushes.tree_id = changeset_pushes.tree_id AND trees.id = pushes.tree_id '
    'AND trees.name = ? GROUP BY head_changeset '
    'ORDER BY changeset_pushes.push_id DESC')


def connection(path):
    return sqlite3.connect(os.path.join(path, '.hg', 'changetracker.db'))


def query_pushes(conn):
    for row in conn.execute(QUERY, ['central']):
        yield row


def last_push_in_month(pushes):
    last_month = None
    for timestamp, buf in pushes:
        year, month = datetime.utcfromtimestamp(timestamp).utctimetuple()[:2]
        if last_month is None:
            last_month = month
        if month == last_month:
            continue
        last_month = month
        yield (year, month, binascii.hexlify(str(buf)))


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('repo_path')
    p.add_argument('outf')
    args = p.parse_args()
    conn = connection(args.repo_path)
    pushes = query_pushes(conn)
    lpm = list(last_push_in_month(pushes))
    with open(args.outf, 'w') as of:
        json.dump(lpm, of, indent=2)
