# snapfetcher

`snapfetcher` fetches snapshot metadata and download URLs from
[PublicNode snapshots](https://www.publicnode.com/snapshots) and
[EthPandaOps Ethereum client snapshots](https://ethpandaops.io/data/snapshots/)
and [PolkaChu Tendermint snapshots](https://www.polkachu.com/tendermint_snapshots).

Ethereum execution clients use EthPandaOps. Tendermint chain names and slugs
listed by PolkaChu use PolkaChu. Other chains use PublicNode.

## Features

- List every chain currently available through the configured snapshot sources.
- Fetch all snapshot URLs by chain name.
- Filter by network, client, snapshot type, archive, and pruned status.
- Output human-readable tables, URL-only output, JSON, or CSV.
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

Write the chain list as a spreadsheet-friendly CSV:

```bash
PYTHONPATH=src python3 -m snapfetcher --list-chains --csv > chains.csv
```

Fetch every snapshot URL for a chain by its chain name:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain "Bitcoin" --url-only
```

Fetch a PolkaChu Tendermint snapshot by chain name or slug:

```bash
PYTHONPATH=src python3 -m snapfetcher --chain "CosmosHub" --url-only
PYTHONPATH=src python3 -m snapfetcher --chain cosmos --url-only
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

This list was fetched from the configured snapshot sources on 2026-06-29.
Snapshot sources can add or remove chains over time, so run
`snapfetcher --list-chains` for the latest live list.

A spreadsheet-friendly CSV copy is available at [chains.csv](chains.csv).

| Chain | ID | Network Names | Clients |
| --- | --- | --- | --- |
| 0g | og | mainnet | chain, geth |
| Agoric | agoric | mainnet | tendermint |
| Akash | akash | mainnet | tendermint |
| Akash Network | akash | mainnet | - |
| Allora | allora | mainnet | tendermint |
| Althea | althea | mainnet | tendermint |
| Andromeda | andromeda | mainnet | tendermint |
| Aptos | aptos | mainnet | - |
| Arbitrum | arbitrum | mainnet, nova, sepolia | - |
| Archway | archway | mainnet | tendermint |
| Arkeo | arkeo | mainnet | tendermint |
| Asset Mantle | assetmantle | mainnet | tendermint |
| AtomOne | atomone | mainnet | - |
| Aura | aura | mainnet | tendermint |
| Avail | avail | mainnet, turing | - |
| Avalanche | avalanche | fuji, mainnet | - |
| Axelar | axelar | mainnet | - |
| Axelar | axelar | mainnet | tendermint |
| Babylon | babylon | mainnet | - |
| Babylon | babylon | mainnet | tendermint |
| Band | band | mainnet | tendermint |
| Base | base | mainnet, sepolia | reth |
| Berachain | berachain | mainnet | beacon, reth |
| BitBadges | bitbadges | mainnet | tendermint |
| Bitcoin | bitcoin | mainnet, testnet | - |
| Bitcoin SV | bsv | mainnet | - |
| Bitsong | bitsong | mainnet | tendermint |
| Bitway | bitway | mainnet | - |
| Bitway | bitway | mainnet | tendermint |
| Blast | blast | mainnet | geth |
| BNB Smart Chain | bsc | mainnet, testnet | geth |
| Canto | canto | mainnet | tendermint |
| Carbon | carbon | mainnet | tendermint |
| Cardano | cardano | mainnet | - |
| Celer Network | celer | mainnet | - |
| Celestia | celestia | mainnet, testnet | - |
| Celestia | celestia | mainnet | tendermint |
| Celo | celo | mainnet | geth |
| Chain4Energy | chain4energy | mainnet | tendermint |
| Cheqd | cheqd | mainnet | - |
| Cheqd | cheqd | mainnet | tendermint |
| Chihuahua | chihuahua | mainnet | tendermint |
| Chiliz | chiliz | mainnet, spicy | - |
| Coreum | coreum | mainnet | tendermint |
| Cosmos | cosmos | mainnet | - |
| CosmosHub | cosmos | mainnet | tendermint |
| Crescent | crescent | mainnet | tendermint |
| Cronos | cronos | mainnet | - |
| Cronos | cronos | mainnet | tendermint |
| Cronos PoS Chain | cronos-pos | mainnet | - |
| Crypto.org | cryptocom | mainnet | tendermint |
| Dash | dash | mainnet, testnet | - |
| Decentr | decentr | mainnet | tendermint |
| DeFiChain | defi | mainnet | - |
| dHealth | dhealth | mainnet | tendermint |
| Dora | dora | mainnet | tendermint |
| Dora Factory | dora | mainnet | - |
| dYdX | dydx | mainnet | - |
| dYdX | dydx | mainnet | tendermint |
| Dymension | dymension | mainnet | tendermint |
| Elys Network | elys | mainnet, testnet | - |
| Empower | empower | mainnet | tendermint |
| Energi | energi | mainnet | - |
| Ethereum | ethereum | mainnet, sepolia, hoodi, holesky, perf-devnet-2, perf-devnet-3 | besu, erigon, geth, nethermind, reth |
| Fetch | fetch | mainnet | tendermint |
| Fetch.ai | fetch | mainnet | - |
| FirmaChain | firmachain | mainnet | tendermint |
| Firo | firo | mainnet | - |
| Fraxtal | fraxtal | hoodi, mainnet | geth |
| Gitopia | gitopia | mainnet | tendermint |
| Gnosis | gnosis | chiado, mainnet | nethermind, teku |
| Gravity | gravity | mainnet | tendermint |
| HAQQ | haqq | mainnet | - |
| Haqq | haqq | mainnet | tendermint |
| Hippo Protocol | hippo | mainnet | tendermint |
| Humans | humans | mainnet | tendermint |
| Initia | initia | mainnet | tendermint |
| Injective | injective | mainnet, testnet | - |
| Injective | injective | mainnet | tendermint |
| interval | interval | mainnet | tendermint |
| Jackal | jackal | mainnet | tendermint |
| Juno | juno | mainnet | - |
| Juno | juno | mainnet | tendermint |
| Kava | kava | mainnet | - |
| Kava | kava | mainnet | tendermint |
| Kujira | kujira | mainnet | tendermint |
| Kusama | kusama | mainnet | - |
| Kyve | kyve | mainnet | tendermint |
| Lava | lava | mainnet | tendermint |
| Linea | linea | mainnet, sepolia | geth |
| Litecoin | litecoin | mainnet | - |
| Lum | lum | mainnet | tendermint |
| Lumera | lumera | mainnet | - |
| Lumera | lumera | mainnet | tendermint |
| Mantle | mantle | mainnet | geth |
| Mantra | mantra | mainnet | tendermint |
| MAP Protocol | map | mainnet | - |
| Medibloc | medibloc | mainnet | - |
| Metis | metis | mainnet, sepolia | l2geth |
| Moonbeam | moonbeam | mainnet | - |
| Moonriver | moonriver | mainnet | - |
| Namada | namada | mainnet | tendermint |
| NEAR Protocol | near | mainnet | - |
| Neutron | neutron | mainnet | - |
| Neutron | neutron | mainnet | tendermint |
| Nibiru | nibiru | mainnet | tendermint |
| Noble | noble | mainnet | tendermint |
| Nolus | nolus | mainnet | tendermint |
| Nomic | nomic | mainnet | tendermint |
| Nym | nym | mainnet | tendermint |
| opBNB | opbnb | mainnet, testnet | geth, reth |
| Optimism | optimism | mainnet, sepolia | reth |
| Oraichain | orai | mainnet | - |
| Oraichain | orai | mainnet | tendermint |
| Osmosis | osmosis | mainnet | - |
| Osmosis | osmosis | mainnet | tendermint |
| Passage | passage | mainnet | tendermint |
| Penumbra | penumbra | mainnet | tendermint |
| Persistence | persistence | mainnet | tendermint |
| Picasso | picasso | mainnet | tendermint |
| PIVX | pivx | mainnet | - |
| Planq | planq | mainnet | tendermint |
| Pocket Network | pocket | mainnet | tendermint |
| Polkadot | polkadot | mainnet | - |
| Polygon | polygon | amoy, mainnet | bor, erigon, heimdall |
| Provenance | provenance | mainnet | tendermint |
| PulseChain | pulsechain | mainnet, testnet | geth, prysm |
| Quicksilver | quicksilver | mainnet | tendermint |
| Radix | radixdlt | babylon | - |
| Regen Network | regen | mainnet | tendermint |
| Saga | saga | mainnet | - |
| Saga | saga | mainnet | tendermint |
| Scroll | scroll | mainnet, sepolia | geth |
| SEDA | seda | mainnet | tendermint |
| Sei | sei | mainnet | - |
| Sei | sei | mainnet | tendermint |
| Sentinel | sentinel | mainnet | - |
| Sentinel dVPN | sentinel | mainnet | tendermint |
| Shentu | shentu | mainnet | tendermint |
| Shido | shido | mainnet | tendermint |
| Sifchain | sifchain | mainnet | tendermint |
| Sommelier | sommelier | mainnet | tendermint |
| Somnia | somnia | mainnet | - |
| Soneium | soneium | mainnet, sepolia | reth |
| Sonic | sonic | mainnet | - |
| Source | source | mainnet | tendermint |
| Starknet | starknet | mainnet, sepolia | juno |
| Story | story | mainnet | client, geth |
| Stride | stride | mainnet | tendermint |
| Sui | sui | mainnet, testnet | - |
| Sunrise | sunrise | mainnet | tendermint |
| Symbol | symbol | mainnet | mongodb, node |
| Syscoin | syscoin | mainnet, testnet | - |
| Tacchain | tacchain | mainnet | tendermint |
| Taiko | taiko | hoodi, mainnet | geth |
| Tempo | tempo | mainnet | - |
| Teritori | teritori | mainnet | tendermint |
| Terra | terra | mainnet | - |
| Terra | terra | mainnet | tendermint |
| Terra Classic | terra-classic | mainnet | - |
| TRON | tron | mainnet | - |
| TX | tx-chain | mainnet | - |
| Umee | umee | mainnet | tendermint |
| Unichain | unichain | mainnet, sepolia | reth |
| Union | union | mainnet | tendermint |
| UnUniFi | ununifi | mainnet | tendermint |
| Verona | verona | mainnet | tendermint |
| Warden | warden | mainnet | - |
| Warden | warden | mainnet | tendermint |
| WEMIX | wemix | mainnet | - |
| Wormchain | wormchain | mainnet | tendermint |
| XPLA | xpla | mainnet | - |
| XPLA | xpla | mainnet | tendermint |
| XRPL EVM Sidechain | xrp | mainnet | tendermint |
| ZetaChain | zetachain | mainnet | tendermint |
| Zigchain | zigchain | mainnet | tendermint |

## CLI Reference

```text
--chain CHAIN          Chain ID or chain name.
--network NETWORK      Network name, such as mainnet, sepolia, testnet, hoodi.
--client CLIENT        Client ID, such as geth, reth, erigon, nethermind, tendermint.
--type TYPE            Snapshot type: base, part, or full.
--archive/--no-archive Filter archive snapshots.
--pruned/--no-pruned   Filter pruned snapshots.
--include-outdated     Include PublicNode entries marked as outdated.
--list-chains          List chain names, IDs, network names, and clients.
--url-only             Print only snapshot URLs.
--json                 Print JSON metadata.
--csv                  Print spreadsheet-friendly CSV output.
--timeout SECONDS      Network timeout. Defaults to 30.
```

## Python API

```python
from snapfetcher import (
    fetch_ethpanda_snapshots,
    fetch_polkachu_snapshots,
    fetch_publicnode_snapshots,
    find_snapshots,
    list_chains,
)

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

cosmoshub = fetch_polkachu_snapshots(chain="CosmosHub")
```

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
```
