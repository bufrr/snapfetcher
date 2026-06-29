# snapfetcher

`snapfetcher` fetches snapshot metadata and download URLs from
[PublicNode snapshots](https://www.publicnode.com/snapshots) and
[EthPandaOps Ethereum client snapshots](https://ethpandaops.io/data/snapshots/).

Ethereum execution clients use EthPandaOps. Other chains use PublicNode.

## Features

- List every chain currently available through the configured snapshot sources.
- Fetch all snapshot URLs by chain name.
- Filter by network, client, snapshot type, archive, and pruned status.
- Output human-readable tables, URL-only output, or JSON.
- Defaults to Ethereum mainnet `geth` from EthPandaOps.

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

Ethereum execution-client snapshots come from EthPandaOps and are returned as a
single `snapshot.tar.zst` URL for the latest available block.

Fetch Ethereum mainnet `reth`:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client reth --no-archive --url-only
```

Fetch all EthPandaOps Ethereum execution-client snapshots for a network:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network hoodi
```

List all chains currently available:

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
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client geth --type full --url-only
```

Return JSON metadata:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --client reth --json
```

## Current Chain Names

This list was fetched from PublicNode on 2026-06-29, with Ethereum execution
clients sourced from EthPandaOps. Snapshot sources can add or remove chains over
time, so run `snapfetcher --list-chains` for the latest live list.

| Chain name | ID |
| --- | --- |
| 0g | og |
| Akash Network | akash |
| Aptos | aptos |
| Arbitrum | arbitrum |
| AtomOne | atomone |
| Avail | avail |
| Avalanche | avalanche |
| Axelar | axelar |
| Babylon | babylon |
| Base | base |
| Berachain | berachain |
| Bitcoin | bitcoin |
| Bitcoin SV | bsv |
| Bitway | bitway |
| Blast | blast |
| BNB Smart Chain | bsc |
| Cardano | cardano |
| Celer Network | celer |
| Celestia | celestia |
| Celo | celo |
| Cheqd | cheqd |
| Chiliz | chiliz |
| Cosmos | cosmos |
| Cronos | cronos |
| Cronos PoS Chain | cronos-pos |
| Dash | dash |
| DeFiChain | defi |
| Dora Factory | dora |
| dYdX | dydx |
| Elys Network | elys |
| Energi | energi |
| Ethereum | ethereum |
| Fetch.ai | fetch |
| Firo | firo |
| Fraxtal | fraxtal |
| Gnosis | gnosis |
| HAQQ | haqq |
| Injective | injective |
| Juno | juno |
| Kava | kava |
| Kusama | kusama |
| Linea | linea |
| Litecoin | litecoin |
| Lumera | lumera |
| Mantle | mantle |
| MAP Protocol | map |
| Medibloc | medibloc |
| Metis | metis |
| Moonbeam | moonbeam |
| Moonriver | moonriver |
| NEAR Protocol | near |
| Neutron | neutron |
| opBNB | opbnb |
| Optimism | optimism |
| Oraichain | orai |
| Osmosis | osmosis |
| PIVX | pivx |
| Polkadot | polkadot |
| Polygon | polygon |
| PulseChain | pulsechain |
| Radix | radixdlt |
| Saga | saga |
| Scroll | scroll |
| Sei | sei |
| Sentinel | sentinel |
| Somnia | somnia |
| Soneium | soneium |
| Sonic | sonic |
| Starknet | starknet |
| Story | story |
| Sui | sui |
| Symbol | symbol |
| Syscoin | syscoin |
| Taiko | taiko |
| Tempo | tempo |
| Terra | terra |
| Terra Classic | terra-classic |
| TRON | tron |
| TX | tx-chain |
| Unichain | unichain |
| Warden | warden |
| WEMIX | wemix |
| XPLA | xpla |

## CLI Reference

```text
--chain CHAIN          Chain ID or chain name.
--network NETWORK      Network name, such as mainnet, sepolia, testnet, hoodi.
--client CLIENT        Client ID, such as geth, reth, erigon, nethermind.
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
from snapfetcher import fetch_ethpanda_snapshots, fetch_publicnode_snapshots, find_snapshots, list_chains

snapshots = fetch_publicnode_snapshots()
chains = list_chains(snapshots)
bitcoin = find_snapshots(snapshots, chain="Bitcoin")

ethereum = fetch_ethpanda_snapshots(network="mainnet", client="reth")
ethereum_reth = find_snapshots(
    ethereum,
    chain="ethereum",
    network="mainnet",
    client="reth",
)
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
```
