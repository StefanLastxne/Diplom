import re

import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

pytestmark = pytest.mark.ui

HOME_URL = "https://changenow.io/en"
RECIPIENT = "0x0d005709871EA64C68038a8Fe4085A026E08cBf6"
TXS_MARK = "/exchange/txs/"

COOKIE = (
    By.CSS_SELECTOR,
    "#onetrust-accept-btn-handler, button.uc-accept-all",
)

EXPLORE = (
    By.XPATH,
    (
        "//button[normalize-space()='Explore'] | "
        "//button[contains(@class,'new-stepper-button') "
        "and contains(.,'Explore')] | "
        "//a[contains(@href,'exchange')]"
    ),
)

IFRAME_ANY = (By.CSS_SELECTOR, "iframe")

RECIPIENT_INPUT = (
    By.XPATH,
    (
        "//input[@id='recipientWallet' or "
        "contains(@placeholder,'payout address') or "
        "contains(@placeholder,'Recipient')]"
    ),
)

CONFIRM = (
    By.CSS_SELECTOR,
    (
        "button.now-button.now-button__green.exchange-stepper--next-button, "
        "button.exchange-stepper--next-button"
    ),
)

TX_PAGE_ANY = (
    By.XPATH,
    (
        "//*[contains(.,'Transaction ID') or contains(.,'Send') or "
        "contains(.,'Deposit') or contains(.,'payin') or "
        "contains(.,'address') or contains(.,'Copy')]"
    ),
)


def _js_click(drv, el):
    drv.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        el,
    )
    drv.execute_script("arguments[0].click();", el)


def _pointer_click(drv, el):
    drv.execute_script(
        """
const el=arguments[0]; el.scrollIntoView({block:'center'});
const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
['pointerover','pointerenter','mouseover','mouseenter',
 'pointermove','mousemove','pointerdown','mousedown',
 'pointerup','mouseup','click']
.forEach(t=>el.dispatchEvent(
    new MouseEvent(t,{bubbles:true,cancelable:true,
                      clientX:x,clientY:y,buttons:1})));
""",
        el,
    )


def _accept_cookies(drv):
    try:
        el = W(drv, 5).until(EC.element_to_be_clickable(COOKIE))
        _js_click(drv, el)
    except Exception:
        pass


def _switch_iframe_if_any(drv):
    drv.switch_to.default_content()
    for f in drv.find_elements(*IFRAME_ANY):
        try:
            drv.switch_to.default_content()
            drv.switch_to.frame(f)
            has_form = drv.find_elements(*CONFIRM) or drv.find_elements(
                By.ID,
                "recipientWallet",
            )
            if has_form:
                return
        except Exception:
            continue
    drv.switch_to.default_content()


def _open_exchange_from_home(drv):
    drv.get(HOME_URL)
    _accept_cookies(drv)
    btn = W(drv, 12).until(EC.element_to_be_clickable(EXPLORE))
    _js_click(drv, btn)
    try:
        W(drv, 12).until(EC.url_contains("/exchange"))
    except Exception:
        pass
    _switch_iframe_if_any(drv)


def _fill_recipient(drv, address: str):
    inp = W(drv, 20).until(EC.visibility_of_element_located(RECIPIENT_INPUT))
    try:
        inp.clear()
    except Exception:
        pass
    inp.send_keys(address)
    inp.send_keys(Keys.TAB)
    return inp


def _click_confirm_hard(drv, wallet_el):
    btn = W(drv, 20).until(EC.presence_of_element_located(CONFIRM))
    try:
        W(drv, 8).until(EC.visibility_of(btn))
    except Exception:
        pass

    try:
        wallet_el.send_keys(Keys.ENTER)
        W(drv, 6).until(EC.url_contains(TXS_MARK))
        return True
    except Exception:
        pass

    try:
        btn.click()
        W(drv, 6).until(EC.url_contains(TXS_MARK))
        return True
    except Exception:
        pass

    try:
        ActionChains(drv).move_to_element(btn).pause(0.1).click(
            btn
        ).perform()
        W(drv, 6).until(EC.url_contains(TXS_MARK))
        return True
    except Exception:
        pass

    try:
        _js_click(drv, btn)
        W(drv, 6).until(EC.url_contains(TXS_MARK))
        return True
    except Exception:
        pass

    try:
        _pointer_click(drv, btn)
        W(drv, 6).until(EC.url_contains(TXS_MARK))
        return True
    except Exception:
        pass

    return False


def _go_to_txs(drv):
    _open_exchange_from_home(drv)
    wallet = _fill_recipient(drv, RECIPIENT)
    ok = _click_confirm_hard(drv, wallet)
    if not ok:
        drv.refresh()
        _accept_cookies(drv)
        _switch_iframe_if_any(drv)
        wallet = _fill_recipient(drv, RECIPIENT)
        ok = _click_confirm_hard(drv, wallet)
        assert ok, "Confirm не привёл к переходу"
    W(drv, 45).until(EC.url_contains(TXS_MARK))
    return drv.current_url


@allure.title("Главная содержит рабочий переход по кнопке Explore")
def test_explore_leads_to_exchange(driver):
    driver.get(HOME_URL)
    _accept_cookies(driver)
    el = W(driver, 12).until(EC.element_to_be_clickable(EXPLORE))
    _js_click(driver, el)
    W(driver, 12).until(EC.url_contains("/exchange"))


@allure.title("После Explore виден input адреса получателя")
def test_recipient_input_visible(driver):
    _open_exchange_from_home(driver)
    W(driver, 15).until(EC.visibility_of_element_located(RECIPIENT_INPUT))


@allure.title("Ввод адреса делает Confirm кликабельной")
def test_confirm_clickable_after_address(driver):
    _open_exchange_from_home(driver)
    _fill_recipient(driver, RECIPIENT)
    W(driver, 15).until(EC.element_to_be_clickable(CONFIRM))


@allure.title("Explore → ввод адреса → Confirm → переход на /exchange/txs/*")
def test_wallet_confirm_flow_to_txs(driver):
    url = _go_to_txs(driver)
    assert TXS_MARK in url


@allure.title("Страница транзакции валидна: есть id и ключевые элементы")
def test_txs_page_has_id_and_blocks(driver):
    url = _go_to_txs(driver)
    m = re.search(r"/exchange/txs/([a-zA-Z0-9_-]+)", url)
    assert m and len(m.group(1)) >= 6, "Не извлекается корректный tx id"
    W(driver, 20).until(EC.presence_of_element_located(TX_PAGE_ANY))
