import argparse
import json

from configparser import ConfigParser
from compare_locales.parser import getParser, Entity
from mercurial.hg import repository
from mercurial.ui import ui
from mercurial.copies import pathcopies
from mercurial.match import match


def matcher(ctx):
    inis = ['browser/locales/l10n.ini', 'mobile/android/locales/l10n.ini']
    done = set()
    dirs = []
    while inis:
        ini = inis.pop()
        if ini not in ctx:
            continue
        cp = ConfigParser()
        cp.read_string(ctx[ini].data().decode('utf-8'))
        dirs += cp.get('compare','dirs').split()
        if 'includes' in cp:
            inis += map(str, cp['includes'].values())
    if not dirs:
        return None
    return match(ctx.repo().root, ctx.repo().root, patterns=[str(d)+'/locales/en-US/**' for d in dirs])


def handle_update(past, now):
    m = matcher(now)
    if not m:
        return
    data = {
        'totals': handle_current(now, m),
        'updates': {}
    }
    stat = past.status(now, match=m)
    copies = {}
    if stat.added:
        copies = pathcopies(past, now)
    for f in stat.modified + stat.added:
        if f not in stat.added or f in copies:
                past_content = past[copies.get(f, f)].data()
        else:
            past_content = ''
                
        update = compare_content(f, past_content, now[f].data())
        if update:
            data['updates'][f] = update
    return data


def compare_content(f, past, now):
    try:
        p = getParser(f)
    except UserWarning:
        return
    p.readContents(past)
    past_entities, past_map = p.parse()
    p.readContents(now)
    now_entities, now_map = p.parse()
    data = {
        'strings': 0,
        'words': 0
    }
    for k in now_map.keys():
        if k in past_map or not isinstance(now_entities[now_map[k]], Entity):
            continue
        data['strings'] += 1
        data['words'] += now_entities[now_map[k]].count_words()
    return data


def handle_current(now, m):
    '''get current translation stats per file'''
    data = {}
    for f in now.manifest().keys():
        if not m(f):
            continue
        try:
            p = getParser(f)
        except UserWarning:
            continue
        p.readContents(now[f].data())
        entities, _ = p.parse()
        data[f] = {
            'strings': len(entities),
            'words': sum(e.count_words() for e in entities if isinstance(e, Entity))
        }
    return data


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('push_data')
    p.add_argument('repo_path')
    p.add_argument('output')
    args = p.parse_args()
    with open(args.push_data) as infile:
        last_push_in_month = json.load(infile)
    repo = repository(ui(), args.repo_path)

    data = []
    for i, (year, month, rev) in enumerate(last_push_in_month):
        now = repo[str(rev)]
        past = repo[str(last_push_in_month[i+1][-1])]
        _d = handle_update(past, now)
        if _d is None:
            break
        _d['year'] = year
        _d['month'] = month
        _d['rev'] = str(rev)
        data.append(_d)

    with open(args.output, 'w') as outf:
        json.dump(data, outf, indent=2)
