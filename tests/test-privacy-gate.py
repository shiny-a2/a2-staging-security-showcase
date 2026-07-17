#!/usr/bin/env python3

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "scripts" / "privacy-gate.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "privacy.yml"
SPEC = importlib.util.spec_from_file_location("showcase_privacy_gate", GATE_PATH)
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)


class ShowcasePrivacyGateTests(unittest.TestCase):
    def rules(self, content: bytes) -> set[str]:
        return GATE.inspect("review.txt", content)

    def test_rejects_network_and_domain_identifiers(self) -> None:
        public_ipv6 = b"2606" + b":4700:4700::1111"
        private_ipv4 = b"192." + b"168.44.9"
        private_domain = b"control" + b"." + b"example-host" + b"." + b"cloud"

        self.assertIn("public-address", self.rules(public_ipv6))
        self.assertIn("private-topology", self.rules(private_ipv4))
        self.assertIn("unapproved-domain", self.rules(private_domain))

    def test_rejects_generic_credentials_without_echoing_them(self) -> None:
        bearer = b"Bearer " + (b"A" * 28)
        database_url = b"postgres" + b"ql://operator:" + (b"p" * 20) + b"@db.example.test/app"

        self.assertIn("bearer-token", self.rules(bearer))
        self.assertIn("database-url-credential", self.rules(database_url))

    def test_allows_documentation_networks_and_domains(self) -> None:
        self.assertEqual(
            self.rules(b"fixture.example.test 192.0.2.25 2001:db8::25"), set()
        )

    def test_release_tags_run_the_complete_privacy_gate(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

        self.assertIn('tags:\n      - "v*"', workflow)
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("python3 scripts/privacy-gate.py", workflow)
        self.assertIn("python3 tests/test-privacy-gate.py", workflow)


if __name__ == "__main__":
    unittest.main()
