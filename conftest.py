import os
import pytest
from dotenv import load_dotenv
from src.api.client import ChangeNowClient
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

load_dotenv()


@pytest.fixture(scope="session")
def cfg():
    return {
        "base": os.getenv("API_BASE", "https://api.changenow.io"),
        "from": os.getenv("FROM", "btc"),
        "to": os.getenv("TO", "eth"),
        "amount": os.getenv("AMOUNT", "0.01"),
        "payout": os.getenv("PAYOUT_ADDRESS", ""),
        "site": os.getenv("SITE_BASE", "https://changenow.io/en"),
    }


@pytest.fixture(scope="session")
def api(cfg):
    return ChangeNowClient(cfg["base"])


@pytest.fixture(scope="session")
def driver(cfg):
    opts = Options()
    if os.getenv("HEADLESS", "1") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    drv.quit()
