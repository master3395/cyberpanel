#!/usr/bin/env python3
"""Verify CloudFlare DNS record fetch for newstargeted.com uses API token auth."""
import json
import os
import sys

sys.path.insert(0, '/usr/local/CyberCP')
os.chdir('/usr/local/CyberCP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CyberCP.settings')

import django
django.setup()

from loginSystem.models import Administrator
from dns.dnsManager import DNSManager
from plogical.dnsUtilities import DNS


def main():
    admin = Administrator.objects.filter(userName='Admin').first()
    assert admin is not None, 'Admin user missing'

    dm = DNSManager()
    dm.admin = admin
    assert dm.loadCFKeys() == 1, 'CloudFlare credentials not loaded'
    assert dm.auth_type == 'api_token', 'expected api_token auth_type, got %r' % dm.auth_type
    assert '@' in dm.email, 'email missing'
    assert len(dm.key) >= 40, 'token looks too short'

    # Legacy inference regression check
    assert DNS.inferCloudFlareAuthType('a@b.com', 'cfut_' + ('x' * 40)) == 'api_token'
    assert DNS.inferCloudFlareAuthType('a@b.com', 'a' * 37) == 'global_key'

    resp = dm.getCurrentRecordsForDomainCloudFlare(admin.pk, {
        'selectedZone': 'newstargeted.com',
        'currentSelection': 'aRecord',
    })
    body = json.loads(resp.content.decode('utf-8'))
    assert body.get('fetchStatus') == 1, body
    assert 'Invalid request headers' not in str(body.get('error_message') or '')
    data = body.get('data')
    if isinstance(data, str):
        data = json.loads(data)
    assert isinstance(data, list) and len(data) > 0, 'expected DNS records'
    print('OK auth=%s records=%s' % (dm.auth_type, len(data)))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('FAIL:', exc, file=sys.stderr)
        raise SystemExit(1)
