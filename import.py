#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import csv
import copy
import os
import subprocess
import six
import shlex
import sys
from mailmanclient import Client
from urllib.error import HTTPError

from collections import OrderedDict


class ProcessError(IOError):
    pass


def cmdrun(cli,
           debug=False,
           shell=True,
           env=None,
           cwd=None,
           wait=True,
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           raise_error=True,
           stdin=None,
           *args,
           **kwargs):
    if cwd is None:
        cwd = os.getcwd()
    if env is None:
        env = copy.deepcopy(os.environ)
    kwargs.setdefault('cwd', cwd)
    kwargs.setdefault('stdout', stdout)
    kwargs.setdefault('stderr', stderr)
    kwargs.setdefault('stdin', stdin)
    kwargs.setdefault('env', env)
    out, err = None, None
    if isinstance(cli, six.string_types):
        cli = shlex.split(cli)
    if debug:
        print(' '.join(cli), file=sys.stderr)
    pr = subprocess.Popen(cli, *args, **kwargs)
    if wait:
        out, err = pr.communicate()
        if raise_error and pr.returncode != 0:
            if out:
                print(out, file=sys.stderr)
            if err:
                print(err, file=sys.stderr)
            raise ProcessError(cli)
    return {'out': out, 'err': err, 'pr': pr}


domain = os.environ['lists_domain']  # lists.foo.com
api_user = os.environ['api_user']  # restadmin
api_pass = os.environ['api_pass']  # secret_password

lists = OrderedDict()
with open('import.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in spamreader:
        if row:
            ml = row[0].split('@')[0].strip()
            mailing = lists.setdefault(ml, {})
            to_add = mailing.setdefault('add', set())
            to_del = mailing.setdefault('delete', set())
            action = row[1].strip()
            if action == 'add':
                members = to_add
            else:
                members = to_del
            mail = row[2].strip()
            if '@' in mail:
                members.add(mail)

client = Client('http://localhost:8001/3.1', api_user, api_pass)
try:
    dom = client.get_domain(domain)
except (HTTPError,) as exc:
    if exc.code != 404:
        raise
    dom = client.create_domain(domain)


def accept_request(ml, member):
    done = None
    for request in ml.requests:
        if request['email'] != member:
            continue
        if member not in [m.email for m in ml.members]:
            ml.accept_request(request['token'])
        else:
            ml.discard_request(request['token'])
        done = True
    return done


for mailing, actions in six.iteritems(lists):
    for action, members in six.iteritems(actions):
        if not members:
            continue
        addr = '{0}@{1}'.format(mailing, domain)
        print("mailing: {0}".format(addr))
        try:
            ml = client.get_list(addr)
        except (HTTPError,) as exc:
            if exc.code != 404:
                raise
            ml = dom.create_list(mailing)
        for member in members:
            if action == 'add':
                print("  + {0}".format(member))
                accepted = accept_request(ml, member)
                if accepted:
                    continue
                elif member in [m.email for m in ml.members]:
                    print("    already in!")
                    continue
                else:
                    ml.subscribe(member)
            elif action == 'delete':
                print("  - {0}".format(member))
                ml.unsubscribe(member)
            accept_request(ml, member)

if os.path.exists('../data/update_postfix.sh'):
    cmdrun('../data/update_postfix.sh')
# vim:set et sts=4 ts=4 tw=80:
