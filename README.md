# snapfetcher

`snapfetcher` fetches snapshot metadata and download URLs from
[PublicNode snapshots](https://www.publicnode.com/snapshots) by default.
Optional Cosmos-family sources are available for explicit multi-source lookups:
[PolkaChu](https://www.polkachu.com/tendermint_snapshots),
[Lavender.Five](https://www.lavenderfive.com/tools), and
[KJNodes](https://services.kjnodes.com/).

## Features

- List every chain currently available through the selected snapshot sources.
- Fetch snapshot URLs by chain name.
- Filter by network, client, snapshot type, archive, and pruned status.
- Keep PublicNode as the default source unless another source is requested.
- For multi-source lookups, filter stale candidates by height, then speed-test the remaining sources.
- Output human-readable tables, URL-only output, JSON, or CSV.
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

Fetch Ethereum mainnet `reth`:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client reth --no-archive --url-only
```

Fetch every PublicNode snapshot for a chain:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain "Bitcoin"
```

Fetch the best Cosmos mainnet source from all configured providers:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Cosmos --network mainnet --source all --url-only
```

Show every Cosmos mainnet candidate instead of selecting one:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Cosmos --network mainnet --source all --no-best-source --csv
```

Fetch from a specific optional source:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Cosmos --network mainnet --source lavender --url-only
```

List all PublicNode chains currently available:

```bash
PYTHONPATH=src python3 -m snapfetcher --list-chains
```

List all chains from every configured source:

```bash
PYTHONPATH=src python3 -m snapfetcher --list-chains --source all
```

Write the chain list as a spreadsheet-friendly CSV:

```bash
PYTHONPATH=src python3 -m snapfetcher --list-chains --csv > chains.csv
```

Filter a specific snapshot type:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --network mainnet --client geth --type part --url-only
```

Return JSON metadata:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain Ethereum --client reth --json
```

## Current Chain Names

This list was fetched from PublicNode on 2026-06-30. PublicNode can add or
remove chains over time, so run `snapfetcher --list-chains` for the latest live
default-source list. Use `--list-chains --source all` to include optional
Cosmos-family sources.

A spreadsheet-friendly CSV copy is available at [chains.csv](chains.csv).

| Chain | ID | Network Names | Clients |
| --- | --- | --- | --- |
| 0g | og | mainnet | chain, geth |
| Akash Network | akash | mainnet | - |
| Aptos | aptos | mainnet | - |
| Arbitrum | arbitrum | mainnet, nova, sepolia | - |
| AtomOne | atomone | mainnet | - |
| Avail | avail | mainnet, turing | - |
| Avalanche | avalanche | fuji, mainnet | - |
| Axelar | axelar | mainnet | - |
| Babylon | babylon | mainnet | - |
| Base | base | mainnet, sepolia | reth |
| Berachain | berachain | mainnet | beacon, reth |
| Bitcoin | bitcoin | mainnet, testnet | - |
| Bitcoin SV | bsv | mainnet | - |
| Bitway | bitway | mainnet | - |
| Blast | blast | mainnet | geth |
| BNB Smart Chain | bsc | mainnet, testnet | geth |
| Cardano | cardano | mainnet | - |
| Celer Network | celer | mainnet | - |
| Celestia | celestia | mainnet, testnet | - |
| Celo | celo | mainnet | geth |
| Cheqd | cheqd | mainnet | - |
| Chiliz | chiliz | mainnet, spicy | - |
| Cosmos | cosmos | mainnet | - |
| Cronos | cronos | mainnet | - |
| Cronos PoS Chain | cronos-pos | mainnet | - |
| Dash | dash | mainnet, testnet | - |
| DeFiChain | defi | mainnet | - |
| Dora Factory | dora | mainnet | - |
| dYdX | dydx | mainnet | - |
| Elys Network | elys | mainnet, testnet | - |
| Energi | energi | mainnet | - |
| Ethereum | ethereum | hoodi, mainnet, sepolia | besu, erigon, geth, lighthouse, nethermind, prysm, reth, teku |
| Fetch.ai | fetch | mainnet | - |
| Firo | firo | mainnet | - |
| Fraxtal | fraxtal | hoodi, mainnet | geth |
| Gnosis | gnosis | chiado, mainnet | nethermind, teku |
| HAQQ | haqq | mainnet | - |
| Injective | injective | mainnet, testnet | - |
| Juno | juno | mainnet | - |
| Kava | kava | mainnet | - |
| Kusama | kusama | mainnet | - |
| Linea | linea | mainnet, sepolia | geth |
| Litecoin | litecoin | mainnet | - |
| Lumera | lumera | mainnet | - |
| Mantle | mantle | mainnet | geth |
| MAP Protocol | map | mainnet | - |
| Medibloc | medibloc | mainnet | - |
| Metis | metis | mainnet, sepolia | l2geth |
| Moonbeam | moonbeam | mainnet | - |
| Moonriver | moonriver | mainnet | - |
| NEAR Protocol | near | mainnet | - |
| Neutron | neutron | mainnet | - |
| opBNB | opbnb | mainnet, testnet | geth, reth |
| Optimism | optimism | mainnet, sepolia | reth |
| Oraichain | orai | mainnet | - |
| Osmosis | osmosis | mainnet | - |
| PIVX | pivx | mainnet | - |
| Polkadot | polkadot | mainnet | - |
| Polygon | polygon | amoy, mainnet | bor, erigon, heimdall |
| PulseChain | pulsechain | mainnet, testnet | geth, prysm |
| Radix | radixdlt | babylon | - |
| Saga | saga | mainnet | - |
| Scroll | scroll | mainnet, sepolia | geth |
| Sei | sei | mainnet | - |
| Sentinel | sentinel | mainnet | - |
| Somnia | somnia | mainnet | - |
| Soneium | soneium | mainnet, sepolia | reth |
| Sonic | sonic | mainnet | - |
| Starknet | starknet | mainnet, sepolia | juno |
| Story | story | mainnet | client, geth |
| Sui | sui | mainnet, testnet | - |
| Symbol | symbol | mainnet | mongodb, node |
| Syscoin | syscoin | mainnet, testnet | - |
| Taiko | taiko | hoodi, mainnet | geth |
| Tempo | tempo | mainnet | - |
| Terra | terra | mainnet | - |
| Terra Classic | terra-classic | mainnet | - |
| TRON | tron | mainnet | - |
| TX | tx-chain | mainnet | - |
| Unichain | unichain | mainnet, sepolia | reth |
| Warden | warden | mainnet | - |
| WEMIX | wemix | mainnet | - |
| XPLA | xpla | mainnet | - |

## CLI Reference

```text
--chain CHAIN          Chain ID or chain name.
--network NETWORK      Network name, such as mainnet, sepolia, testnet, hoodi.
--client CLIENT        Client ID, such as geth, reth, erigon, nethermind.
--type TYPE            Snapshot type: base, part, or full.
--archive/--no-archive Filter archive snapshots.
--pruned/--no-pruned   Filter pruned snapshots.
--include-outdated     Include PublicNode entries marked as outdated.
--list-chains          List chain names, IDs, network names, and clients.
--url-only             Print only snapshot URLs.
--json                 Print JSON metadata.
--csv                  Print spreadsheet-friendly CSV output.
--source SOURCE        Source to query: publicnode, polkachu, lavender, kjnodes, or all.
--best-source/--no-best-source
                       For multiple sources, choose the best source after freshness filtering.
--max-height-lag N     Maximum block-height lag from the freshest candidate before speed testing.
--timeout SECONDS      Network timeout. Defaults to 30.
```

## Python API

```python
from snapfetcher import (
    fetch_kjnodes_snapshots,
    fetch_lavender_snapshots,
    fetch_polkachu_snapshots,
    fetch_publicnode_snapshots,
    find_snapshots,
    list_chains,
    select_best_source,
)

snapshots = fetch_publicnode_snapshots()
chains = list_chains(snapshots)
bitcoin = find_snapshots(snapshots, chain="Bitcoin")
ethereum_reth = find_snapshots(
    snapshots,
    chain="ethereum",
    network="mainnet",
    client="reth",
)

cosmos_candidates = []
cosmos_candidates.extend(find_snapshots(snapshots, chain="Cosmos", network="mainnet"))
cosmos_candidates.extend(fetch_polkachu_snapshots(chain="Cosmos"))
cosmos_candidates.extend(fetch_lavender_snapshots(chain="Cosmos", network="mainnet"))
cosmos_candidates.extend(fetch_kjnodes_snapshots(chain="Cosmos", network="mainnet"))
best_cosmos_source = select_best_source(cosmos_candidates)
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
```
