from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class HomePage:
    """
    Простой PageObject главной/экшен-страниц ChangeNOW.
    Используется вспомогательно. Тесты могут работать и без него.
    """

    HOME_URL = "https://changenow.io/en"
    TXS_MARK = "/exchange/txs/"

    COOKIE_BTN = (
        By.CSS_SELECTOR,
        "#onetrust-accept-btn-handler, button.uc-accept-all",
    )

    EXPLORE_BTN = (
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

    CONFIRM_BTN = (
        By.CSS_SELECTOR,
        (
            "button.now-button.now-button__green."
            "exchange-stepper--next-button, "
            "button.exchange-stepper--next-button"
        ),
    )

    def __init__(self, driver: WebDriver):
        self.d = driver

    def open(self) -> None:
        self.d.get(self.HOME_URL)

    def _js_click(self, el) -> None:
        self.d.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", el
        )
        self.d.execute_script("arguments[0].click();", el)

    def accept_cookies(self) -> None:
        try:
            btn = W(self.d, 5).until
            (EC.element_to_be_clickable(self.COOKIE_BTN))
            self._js_click(btn)
        except Exception:
            pass

    def open_exchange(self) -> None:
        btn = W(self.d, 12).until(EC.element_to_be_clickable(self.EXPLORE_BTN))
        self._js_click(btn)

    def switch_iframe_if_any(self) -> None:
        self.d.switch_to.default_content()
        frames = self.d.find_elements(*self.IFRAME_ANY)
        for f in frames:
            try:
                self.d.switch_to.default_content()
                self.d.switch_to.frame(f)
                has_form = self.d.find_elements(*self.CONFIRM_BTN) or (
                    self.d.find_elements(*self.RECIPIENT_INPUT)
                )
                if has_form:
                    return
            except Exception:
                continue
        self.d.switch_to.default_content()

    def recipient_input(self):
        return W(self.d, 20).until(
            EC.visibility_of_element_located(self.RECIPIENT_INPUT)
        )

    def enter_recipient(self, address: str) -> None:
        inp = self.recipient_input()
        try:
            inp.clear()
        except Exception:
            pass
        inp.send_keys(address)
        inp.send_keys(Keys.TAB)

    def click_confirm(self) -> None:
        btn = W(self.d, 20).until(
            EC.element_to_be_clickable(self.CONFIRM_BTN)
        )
        try:
            btn.click()
        except Exception:
            ActionChains(self.d).move_to_element(btn).pause(0.1).click(
                btn
            ).perform()
        try:
            self._js_click(btn)
        except Exception:
            pass

    def wait_transaction(self, timeout: int = 45) -> str:
        W(self.d, timeout).until(EC.url_contains(self.TXS_MARK))
        return self.d.current_url
