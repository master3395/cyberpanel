#!/usr/bin/env python
import os, sys, unittest
sys.path.insert(0, '/usr/local/CyberCP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CyberCP.settings')
import django
django.setup()
from plogical.dnsUtilities import DNS

class CloudFlareClientTests(unittest.TestCase):
    def test_api_token_auth(self):
        cf = DNS.createCloudFlareClient('', 'tok_abc', 'api_token')
        self.assertIsNotNone(cf)

    def test_global_key_requires_email(self):
        with self.assertRaises(ValueError):
            DNS.createCloudFlareClient('', 'key', 'global_key')

    def test_invalid_auth_type_falls_back(self):
        cf = DNS.createCloudFlareClient('a@b.com', 'secret_not_a_global_key', 'bogus')
        self.assertIsNotNone(cf)

    def test_infer_api_token_when_email_present_but_secret_is_token(self):
        # Regression: legacy 3-line files with email + API token must not use Global Key headers.
        auth = DNS.inferCloudFlareAuthType('user@example.com', 'cfu' + ('x' * 50))
        self.assertEqual(auth, 'api_token')
        cf = DNS.createCloudFlareClient('user@example.com', 'cfu' + ('x' * 50), None)
        self.assertIsNotNone(cf)

    def test_infer_global_key_for_37_hex(self):
        secret = 'a' * 37
        self.assertEqual(DNS.inferCloudFlareAuthType('user@example.com', secret), 'global_key')

if __name__ == '__main__':
    unittest.main()
