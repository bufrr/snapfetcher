import unittest

from snapfetcher.polkachu import (
    extract_polkachu_chains,
    extract_polkachu_snapshot,
    fetch_polkachu_snapshots,
    find_polkachu_chain,
    polkachu_chain_summaries,
)


class PolkachuTest(unittest.TestCase):
    def test_extracts_supported_tendermint_chains(self):
        chains = extract_polkachu_chains(_landing_html())

        self.assertEqual([chain.slug for chain in chains], ["akash", "cosmos"])
        self.assertEqual([chain.name for chain in chains], ["Akash", "CosmosHub"])

    def test_finds_by_name_or_slug(self):
        chains = extract_polkachu_chains(_landing_html())

        self.assertEqual(find_polkachu_chain(chains, "CosmosHub").slug, "cosmos")
        self.assertEqual(find_polkachu_chain(chains, "cosmos").name, "CosmosHub")
        self.assertIsNone(find_polkachu_chain(chains, "Ethereum"))

    def test_extracts_snapshot_from_detail_page(self):
        chain = find_polkachu_chain(extract_polkachu_chains(_landing_html()), "cosmos")

        snapshot = extract_polkachu_snapshot(_detail_html(), chain)

        self.assertEqual(snapshot.source, "polkachu")
        self.assertEqual(snapshot.currency_id, "cosmos")
        self.assertEqual(snapshot.currency_name, "CosmosHub")
        self.assertEqual(snapshot.network_name, "mainnet")
        self.assertEqual(snapshot.client_id, "tendermint")
        self.assertEqual(snapshot.snapshot_type, "full")
        self.assertEqual(snapshot.block_heights, (31798367,))
        self.assertEqual(snapshot.compressed_size_label, "21.0 GB")
        self.assertEqual(snapshot.node_version, "v27.4.0")
        self.assertEqual(
            snapshot.url,
            "https://snapshots.polkachu.com/snapshots/cosmos/cosmos_31798367.tar.lz4",
        )
        self.assertTrue(snapshot.is_pruned)

    def test_fetches_snapshot_with_existing_chain_list(self):
        chains = extract_polkachu_chains(_landing_html())
        requested_urls = []

        def fetch_text(url, timeout):
            requested_urls.append(url)
            return _detail_html()

        snapshots = fetch_polkachu_snapshots(
            chain="CosmosHub",
            chains=chains,
            fetch_text=fetch_text,
        )

        self.assertEqual(len(snapshots), 1)
        self.assertEqual(requested_urls, ["https://www.polkachu.com/tendermint_snapshots/cosmos"])

    def test_builds_chain_summaries(self):
        summaries = polkachu_chain_summaries(extract_polkachu_chains(_landing_html()))

        self.assertEqual(summaries[0].currency_name, "Akash")
        self.assertEqual(summaries[0].networks, ("mainnet",))
        self.assertEqual(summaries[0].clients, ("tendermint",))


def _landing_html():
    return """
    <a href="https://www.polkachu.com/tendermint_snapshots/akash">Akash</a>
    <a href="https://www.polkachu.com/tendermint_snapshots/cosmos">CosmosHub</a>
    """


def _detail_html():
    return """
    <title>CosmosHub Node Snapshot | Polkachu</title>
    <p>
      <span class="font-semibold">Chain ID</span>: cosmoshub-4
      | <span class="font-semibold">Current Node Version</span>: v27.4.0
    </p>
    <table>
      <thead>
        <tr>
          <th>Latest</th>
          <th>Block Height</th>
          <th>Size</th>
          <th>Timestamp</th>
          <th>Download</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td></td>
          <td>31798367</td>
          <td>21 GB</td>
          <td>1 hour ago</td>
          <td>
            <a href="https://snapshots.polkachu.com/snapshots/cosmos/cosmos_31798367.tar.lz4">
              cosmos_31798367.tar.lz4
            </a>
          </td>
        </tr>
      </tbody>
    </table>
    """


if __name__ == "__main__":
    unittest.main()
