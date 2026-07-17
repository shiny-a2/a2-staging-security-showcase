#!/usr/bin/env python3

import importlib.util
from pathlib import Path
import re
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

    def workflow_block(self, workflow: str, header: str) -> str:
        lines = workflow.splitlines()
        matches = [index for index, line in enumerate(lines) if line == header]
        self.assertEqual(len(matches), 1, f"expected one active {header!r} block")
        start = matches[0]
        indentation = len(header) - len(header.lstrip(" "))
        block = [header]

        for line in lines[start + 1 :]:
            stripped = line.strip()
            if stripped and not line.lstrip().startswith("#"):
                line_indentation = len(line) - len(line.lstrip(" "))
                if line_indentation <= indentation:
                    break
            block.append(line)
        return "\n".join(block)

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

    def assert_release_workflow(self, workflow: str) -> None:
        push = self.workflow_block(workflow, "  push:")
        privacy = self.workflow_block(workflow, "  privacy:")
        active_privacy_lines = [
            line.strip()
            for line in privacy.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

        self.assertIn('    tags:\n      - "v*"', push)
        self.assertEqual(active_privacy_lines.count("fetch-depth: 0"), 1)
        self.assertEqual(active_privacy_lines.count("persist-credentials: false"), 1)
        self.assertEqual(
            active_privacy_lines.count("run: python3 scripts/privacy-gate.py"), 1
        )
        self.assertEqual(
            active_privacy_lines.count("run: python3 tests/test-privacy-gate.py"), 1
        )
        self.assertFalse(
            any(
                re.match(r"^(?:if|continue-on-error)\s*:", line)
                for line in active_privacy_lines
            )
        )
        self.assertNotRegex(
            "\n".join(active_privacy_lines),
            r"(?:\|\|\s*true\b|;\s*true\b|\bset\s+\+e\b)",
        )

    def test_release_tags_run_the_complete_privacy_gate(self) -> None:
        self.assert_release_workflow(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_release_workflow_rejects_suppression_mutations(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        mutations = {
            "missing push event": workflow.replace(
                "  push:", "  workflow_dispatch:", 1
            ),
            "wrong tag selector": workflow.replace('- "v*"', '- "release-*"', 1),
            "commented gate": workflow.replace(
                "        run: python3 scripts/privacy-gate.py",
                "        # run: python3 scripts/privacy-gate.py",
                1,
            ),
            "disabled job": workflow.replace(
                "  privacy:\n", "  privacy:\n    if: false\n", 1
            ),
            "ignored step failure": workflow.replace(
                "      - name: Reject sensitive showcase content\n",
                "      - name: Reject sensitive showcase content\n"
                "        continue-on-error: true\n",
                1,
            ),
            "shell suppression": workflow.replace(
                "run: python3 scripts/privacy-gate.py",
                "run: python3 scripts/privacy-gate.py || true",
                1,
            ),
            "shallow checkout": workflow.replace("fetch-depth: 0", "fetch-depth: 1", 1),
        }

        for label, mutation in mutations.items():
            with self.subTest(label=label):
                self.assertNotEqual(mutation, workflow)
                with self.assertRaises(AssertionError):
                    self.assert_release_workflow(mutation)


if __name__ == "__main__":
    unittest.main()
