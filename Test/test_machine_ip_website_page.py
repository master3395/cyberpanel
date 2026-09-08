#!/usr/bin/env python3
"""Verify machine_ip helper and CyberPanel website detail page for newstargeted.com."""
import os
import sys

sys.path.insert(0, '/usr/local/CyberCP')
os.chdir('/usr/local/CyberCP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CyberCP.settings')

import django
django.setup()

from plogical.machine_ip import read_machine_ip
from plogical.acl import ACLManager
from django.test import Client
from loginSystem.models import Administrator


def main():
    ip = read_machine_ip()
    assert ip and ip != '127.0.0.1', f'unexpected machine IP: {ip!r}'
    assert ACLManager.GetServerIP() == ip

    admin = Administrator.objects.filter(userName='admin').first() or Administrator.objects.filter(pk=1).first()
    assert admin is not None, 'no admin user'

    client = Client()
    session = client.session
    session['userID'] = admin.pk
    session.save()
    client.cookies['sessionid'] = session.session_key

    response = client.get('/websites/newstargeted.com')
    body = response.content.decode('utf-8', 'replace')
    assert response.status_code == 200, f'status={response.status_code}'
    assert 'Server Error' not in body
    assert 'newstargeted.com' in body
    print('OK machine_ip=%s status=%s' % (ip, response.status_code))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('FAIL:', exc, file=sys.stderr)
        raise SystemExit(1)
