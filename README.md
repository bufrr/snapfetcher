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

```text
chain               id             snapshots  networks                                                        clients                             
------------------  -------------  ---------  --------------------------------------------------------------  ------------------------------------
0g                  og             3          mainnet                                                         chain, geth                         
Agoric              agoric         1          mainnet                                                         tendermint                          
Akash               akash          1          mainnet                                                         tendermint                          
Akash Network       akash          1          mainnet                                                         -                                   
Allora              allora         1          mainnet                                                         tendermint                          
Althea              althea         1          mainnet                                                         tendermint                          
Andromeda           andromeda      1          mainnet                                                         tendermint                          
Aptos               aptos          1          mainnet                                                         -                                   
Arbitrum            arbitrum       6          mainnet, nova, sepolia                                          -                                   
Archway             archway        1          mainnet                                                         tendermint                          
Arkeo               arkeo          1          mainnet                                                         tendermint                          
Asset Mantle        assetmantle    1          mainnet                                                         tendermint                          
AtomOne             atomone        1          mainnet                                                         -                                   
Aura                aura           1          mainnet                                                         tendermint                          
Avail               avail          2          mainnet, turing                                                 -                                   
Avalanche           avalanche      4          fuji, mainnet                                                   -                                   
Axelar              axelar         1          mainnet                                                         -                                   
Axelar              axelar         1          mainnet                                                         tendermint                          
Babylon             babylon        1          mainnet                                                         -                                   
Babylon             babylon        1          mainnet                                                         tendermint                          
Band                band           1          mainnet                                                         tendermint                          
Base                base           6          mainnet, sepolia                                                reth                                
Berachain           berachain      2          mainnet                                                         beacon, reth                        
BitBadges           bitbadges      1          mainnet                                                         tendermint                          
Bitcoin             bitcoin        4          mainnet, testnet                                                -                                   
Bitcoin SV          bsv            1          mainnet                                                         -                                   
Bitsong             bitsong        1          mainnet                                                         tendermint                          
Bitway              bitway         1          mainnet                                                         -                                   
Bitway              bitway         1          mainnet                                                         tendermint                          
Blast               blast          2          mainnet                                                         geth                                
BNB Smart Chain     bsc            4          mainnet, testnet                                                geth                                
Canto               canto          1          mainnet                                                         tendermint                          
Carbon              carbon         1          mainnet                                                         tendermint                          
Cardano             cardano        1          mainnet                                                         -                                   
Celer Network       celer          1          mainnet                                                         -                                   
Celestia            celestia       2          mainnet, testnet                                                -                                   
Celestia            celestia       1          mainnet                                                         tendermint                          
Celo                celo           2          mainnet                                                         geth                                
Chain4Energy        chain4energy   1          mainnet                                                         tendermint                          
Cheqd               cheqd          1          mainnet                                                         -                                   
Cheqd               cheqd          1          mainnet                                                         tendermint                          
Chihuahua           chihuahua      1          mainnet                                                         tendermint                          
Chiliz              chiliz         4          mainnet, spicy                                                  -                                   
Coreum              coreum         1          mainnet                                                         tendermint                          
Cosmos              cosmos         1          mainnet                                                         -                                   
CosmosHub           cosmos         1          mainnet                                                         tendermint                          
Crescent            crescent       1          mainnet                                                         tendermint                          
Cronos              cronos         1          mainnet                                                         -                                   
Cronos              cronos         1          mainnet                                                         tendermint                          
Cronos PoS Chain    cronos-pos     1          mainnet                                                         -                                   
Crypto.org          cryptocom      1          mainnet                                                         tendermint                          
Dash                dash           3          mainnet, testnet                                                -                                   
Decentr             decentr        1          mainnet                                                         tendermint                          
DeFiChain           defi           1          mainnet                                                         -                                   
dHealth             dhealth        1          mainnet                                                         tendermint                          
Dora                dora           1          mainnet                                                         tendermint                          
Dora Factory        dora           1          mainnet                                                         -                                   
dYdX                dydx           1          mainnet                                                         -                                   
dYdX                dydx           1          mainnet                                                         tendermint                          
Dymension           dymension      1          mainnet                                                         tendermint                          
Elys Network        elys           2          mainnet, testnet                                                -                                   
Empower             empower        1          mainnet                                                         tendermint                          
Energi              energi         1          mainnet                                                         -                                   
Ethereum            ethereum       30         mainnet, sepolia, hoodi, holesky, perf-devnet-2, perf-devnet-3  besu, erigon, geth, nethermind, reth
Fetch               fetch          1          mainnet                                                         tendermint                          
Fetch.ai            fetch          1          mainnet                                                         -                                   
FirmaChain          firmachain     1          mainnet                                                         tendermint                          
Firo                firo           2          mainnet                                                         -                                   
Fraxtal             fraxtal        4          hoodi, mainnet                                                  geth                                
Gitopia             gitopia        1          mainnet                                                         tendermint                          
Gnosis              gnosis         4          chiado, mainnet                                                 nethermind, teku                    
Gravity             gravity        1          mainnet                                                         tendermint                          
HAQQ                haqq           1          mainnet                                                         -                                   
Haqq                haqq           1          mainnet                                                         tendermint                          
Hippo Protocol      hippo          1          mainnet                                                         tendermint                          
Humans              humans         1          mainnet                                                         tendermint                          
Initia              initia         1          mainnet                                                         tendermint                          
Injective           injective      2          mainnet, testnet                                                -                                   
Injective           injective      1          mainnet                                                         tendermint                          
interval            interval       1          mainnet                                                         tendermint                          
Jackal              jackal         1          mainnet                                                         tendermint                          
Juno                juno           1          mainnet                                                         -                                   
Juno                juno           1          mainnet                                                         tendermint                          
Kava                kava           1          mainnet                                                         -                                   
Kava                kava           1          mainnet                                                         tendermint                          
Kujira              kujira         1          mainnet                                                         tendermint                          
Kusama              kusama         1          mainnet                                                         -                                   
Kyve                kyve           1          mainnet                                                         tendermint                          
Lava                lava           1          mainnet                                                         tendermint                          
Linea               linea          3          mainnet, sepolia                                                geth                                
Litecoin            litecoin       2          mainnet                                                         -                                   
Lum                 lum            1          mainnet                                                         tendermint                          
Lumera              lumera         1          mainnet                                                         -                                   
Lumera              lumera         1          mainnet                                                         tendermint                          
Mantle              mantle         2          mainnet                                                         geth                                
Mantra              mantra         1          mainnet                                                         tendermint                          
MAP Protocol        map            1          mainnet                                                         -                                   
Medibloc            medibloc       1          mainnet                                                         -                                   
Metis               metis          4          mainnet, sepolia                                                l2geth                              
Moonbeam            moonbeam       2          mainnet                                                         -                                   
Moonriver           moonriver      2          mainnet                                                         -                                   
Namada              namada         1          mainnet                                                         tendermint                          
NEAR Protocol       near           1          mainnet                                                         -                                   
Neutron             neutron        1          mainnet                                                         -                                   
Neutron             neutron        1          mainnet                                                         tendermint                          
Nibiru              nibiru         1          mainnet                                                         tendermint                          
Noble               noble          1          mainnet                                                         tendermint                          
Nolus               nolus          1          mainnet                                                         tendermint                          
Nomic               nomic          1          mainnet                                                         tendermint                          
Nym                 nym            1          mainnet                                                         tendermint                          
opBNB               opbnb          6          mainnet, testnet                                                geth, reth                          
Optimism            optimism       4          mainnet, sepolia                                                reth                                
Oraichain           orai           1          mainnet                                                         -                                   
Oraichain           orai           1          mainnet                                                         tendermint                          
Osmosis             osmosis        1          mainnet                                                         -                                   
Osmosis             osmosis        1          mainnet                                                         tendermint                          
Passage             passage        1          mainnet                                                         tendermint                          
Penumbra            penumbra       1          mainnet                                                         tendermint                          
Persistence         persistence    1          mainnet                                                         tendermint                          
Picasso             picasso        1          mainnet                                                         tendermint                          
PIVX                pivx           2          mainnet                                                         -                                   
Planq               planq          1          mainnet                                                         tendermint                          
Pocket Network      pocket         1          mainnet                                                         tendermint                          
Polkadot            polkadot       1          mainnet                                                         -                                   
Polygon             polygon        11         amoy, mainnet                                                   bor, erigon, heimdall               
Provenance          provenance     1          mainnet                                                         tendermint                          
PulseChain          pulsechain     6          mainnet, testnet                                                geth, prysm                         
Quicksilver         quicksilver    1          mainnet                                                         tendermint                          
Radix               radixdlt       1          babylon                                                         -                                   
Regen Network       regen          1          mainnet                                                         tendermint                          
Saga                saga           1          mainnet                                                         -                                   
Saga                saga           1          mainnet                                                         tendermint                          
Scroll              scroll         4          mainnet, sepolia                                                geth                                
SEDA                seda           1          mainnet                                                         tendermint                          
Sei                 sei            1          mainnet                                                         -                                   
Sei                 sei            1          mainnet                                                         tendermint                          
Sentinel            sentinel       1          mainnet                                                         -                                   
Sentinel dVPN       sentinel       1          mainnet                                                         tendermint                          
Shentu              shentu         1          mainnet                                                         tendermint                          
Shido               shido          1          mainnet                                                         tendermint                          
Sifchain            sifchain       1          mainnet                                                         tendermint                          
Sommelier           sommelier      1          mainnet                                                         tendermint                          
Somnia              somnia         1          mainnet                                                         -                                   
Soneium             soneium        2          mainnet, sepolia                                                reth                                
Sonic               sonic          1          mainnet                                                         -                                   
Source              source         1          mainnet                                                         tendermint                          
Starknet            starknet       2          mainnet, sepolia                                                juno                                
Story               story          3          mainnet                                                         client, geth                        
Stride              stride         1          mainnet                                                         tendermint                          
Sui                 sui            4          mainnet, testnet                                                -                                   
Sunrise             sunrise        1          mainnet                                                         tendermint                          
Symbol              symbol         2          mainnet                                                         mongodb, node                       
Syscoin             syscoin        3          mainnet, testnet                                                -                                   
Tacchain            tacchain       1          mainnet                                                         tendermint                          
Taiko               taiko          4          hoodi, mainnet                                                  geth                                
Tempo               tempo          1          mainnet                                                         -                                   
Teritori            teritori       1          mainnet                                                         tendermint                          
Terra               terra          1          mainnet                                                         -                                   
Terra               terra          1          mainnet                                                         tendermint                          
Terra Classic       terra-classic  1          mainnet                                                         -                                   
TRON                tron           1          mainnet                                                         -                                   
TX                  tx-chain       1          mainnet                                                         -                                   
Umee                umee           1          mainnet                                                         tendermint                          
Unichain            unichain       2          mainnet, sepolia                                                reth                                
Union               union          1          mainnet                                                         tendermint                          
UnUniFi             ununifi        1          mainnet                                                         tendermint                          
Verona              verona         1          mainnet                                                         tendermint                          
Warden              warden         1          mainnet                                                         -                                   
Warden              warden         1          mainnet                                                         tendermint                          
WEMIX               wemix          1          mainnet                                                         -                                   
Wormchain           wormchain      1          mainnet                                                         tendermint                          
XPLA                xpla           1          mainnet                                                         -                                   
XPLA                xpla           1          mainnet                                                         tendermint                          
XRPL EVM Sidechain  xrp            1          mainnet                                                         tendermint                          
ZetaChain           zetachain      1          mainnet                                                         tendermint                          
Zigchain            zigchain       1          mainnet                                                         tendermint
```

## CLI Reference

```text
--chain CHAIN          Chain ID or chain name.
--network NETWORK      Network name, such as mainnet, sepolia, testnet, hoodi.
--client CLIENT        Client ID, such as geth, reth, erigon, nethermind, tendermint.
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
