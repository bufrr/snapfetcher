# snapfetcher

`snapfetcher` fetches snapshot metadata and download URLs from
[PublicNode snapshots](https://www.publicnode.com/snapshots).

It reads the live PublicNode snapshots page, discovers the current Next.js data
endpoint, and parses the snapshot JSON behind the table.

## Features

- List every chain currently available on PublicNode.
- Fetch all snapshot URLs by chain name.
- Filter by network, client, snapshot type, archive, and pruned status.
- Output human-readable tables, URL-only output, or JSON.
- Defaults to Ethereum mainnet `geth`.

## Usage

Run from the checkout without installing:

```bash
PYTHONPATH=src python3 -m snapfetcher
```

Install locally to expose the `snapfetcher` command:

```bash
python3 -m pip install -e .
snapfetcher --url-only
```

## Examples

Default Ethereum mainnet `geth` lookup:

```bash
PYTHONPATH=src python3 -m snapfetcher --url-only
```

PublicNode publishes Ethereum mainnet `geth` as split `base` and `part`
archives, so the default command returns both segment URLs.

Fetch Ethereum mainnet `reth`:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client reth --no-archive --url-only
```

List all chains currently available in PublicNode snapshots:

```bash
PYTHONPATH=src python3 -m snapfetcher --list-chains
```

Fetch every snapshot URL for a chain by its chain name:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain "Bitcoin" --url-only
```

When `--chain` is supplied without `--network` or `--client`, `snapfetcher`
returns all matching networks and clients for that chain name.

Filter a specific snapshot type:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client geth --type part --url-only
```

Return JSON metadata:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --client reth --json
```

## CLI Reference

```text
--chain CHAIN          PublicNode currency ID or chain name.
--network NETWORK      Network name, such as mainnet, sepolia, testnet, hoodi.
--client CLIENT        Client ID, such as geth, reth, erigon, lighthouse.
--type TYPE            Snapshot type: base, part, or full.
--archive/--no-archive Filter archive snapshots.
--pruned/--no-pruned   Filter pruned snapshots.
--include-outdated     Include PublicNode entries marked as outdated.
--list-chains          List available chain names.
--url-only             Print only snapshot URLs.
--json                 Print JSON metadata.
--timeout SECONDS      Network timeout. Defaults to 30.
```

## Python API

```python
from snapfetcher import fetch_publicnode_snapshots, find_snapshots, list_chains

snapshots = fetch_publicnode_snapshots()
chains = list_chains(snapshots)
bitcoin = find_snapshots(snapshots, chain="Bitcoin")
ethereum_reth = find_snapshots(
    snapshots,
    chain="Ethereum",
    network="mainnet",
    client="reth",
    archive=False,
)
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
```
