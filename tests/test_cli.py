import unittest

from snapfetcher.cli import _chain_to_dict, _format_chain_table
from snapfetcher.publicnode import ChainSummary


class CliTest(unittest.TestCase):
    def test_chain_table_includes_network_names_without_counts(self):
        table = _format_chain_table(
            [
                ChainSummary(
                    currency_id="bitcoin",
                    currency_name="Bitcoin",
                    snapshot_count=4,
                    networks=("mainnet", "testnet"),
                    clients=(),
                )
            ]
        )

        header = table.splitlines()[0]

        self.assertNotIn("snapshots", header)
        self.assertNotIn("network_count", header)
        self.assertIn("network_names", table)
        self.assertIn("Bitcoin", table)
        self.assertIn("mainnet, testnet", table)

    def test_chain_json_keeps_summary_fields(self):
        payload = _chain_to_dict(
            ChainSummary(
                currency_id="ethereum",
                currency_name="Ethereum",
                snapshot_count=30,
                networks=("mainnet", "sepolia"),
                clients=("geth", "reth"),
            )
        )

        self.assertEqual(payload["networkCount"], 2)
        self.assertEqual(payload["networkNames"], ["mainnet", "sepolia"])
        self.assertEqual(payload["networks"], ["mainnet", "sepolia"])


if __name__ == "__main__":
    unittest.main()
