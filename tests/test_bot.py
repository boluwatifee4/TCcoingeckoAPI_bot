import pytest
import requests
from bima_trending_coins_bot import fetch_trending_data, process_trending_coins, process_trending_nfts

def test_fetch_trending_data(monkeypatch):
    class MockResponse:
        @staticmethod
        def json():
            return {
                "coins": [
                    {"item": {"name": "Bitcoin", "symbol": "btc", "id": "bitcoin", "market_cap_rank": 1, "data": {"market_cap_btc": 1, "market_cap": 1000000000, "total_volume": 100000000, "total_volume_btc": 10}}},
                    # Add more mock coin data if necessary
                ],
                "nfts": [
                    {"name": "NFT 1", "symbol": "nft1", "nft_contract_id": "nft1_id", "floor_price": 1, "floor_price_in_usd_24h_percentage_change": 0.5, "h24_volume": 1000, "h24_average_sale_price": 100},
                    # Add more mock NFT data if necessary
                ]
            }
        
        @property
        def status_code(self):
            return 200

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())

    coins, nfts = fetch_trending_data()
    assert len(coins) > 0
    assert len(nfts) > 0

def test_process_trending_coins():
    coins = [
        {"item": {"name": "Bitcoin", "symbol": "btc", "id": "bitcoin", "market_cap_rank": 1, "data": {"market_cap_btc": 1, "market_cap": 1000000000, "total_volume": 100000000, "total_volume_btc": 10}}}
    ]
    processed_coins = process_trending_coins(coins)
    assert len(processed_coins) == 1
    assert processed_coins[0]["name"] == "Bitcoin"
    assert processed_coins[0]["symbol"] == "btc"

def test_process_trending_nfts():
    nfts = [
        {"name": "NFT 1", "symbol": "nft1", "nft_contract_id": "nft1_id", "floor_price": 1, "floor_price_in_usd_24h_percentage_change": 0.5, "h24_volume": 1000, "h24_average_sale_price": 100}
    ]
    processed_nfts = process_trending_nfts(nfts)
    assert len(processed_nfts) == 1
    assert processed_nfts[0]["name"] == "NFT 1"
    assert processed_nfts[0]["symbol"] == "nft1"
