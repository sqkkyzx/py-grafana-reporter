import logging
from typing import Literal

from playwright.sync_api import sync_playwright, expect


class GrafanaRender:
    def __init__(self, token: str):
        self.token:str = token

        self._headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange",
            "cache-control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            'Authorization': f'Bearer {self.token}'
        }

    def snapshot(self, url: str, width:int=762, height:int=400, height_offset:int=150,  auto_height=True, hide_class:list = None, filetype: Literal["jpeg", "png"]= "png") -> (str, bytes):
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            browser_page = browser.new_page()
            browser_page.set_extra_http_headers(self._headers)
            browser_page.set_viewport_size({"width": width, "height": height})

            browser_page.goto(url)
            browser_page.wait_for_load_state('networkidle')

            logging.debug(browser_page.content())

            if auto_height and "viewPanel" not in url:
                try:
                    # 获取到 .react-grid-layout 的高度并加上一定偏移作为真实高度，然后重新设置窗口大小
                    height = browser_page.evaluate("document.querySelector('.react-grid-layout').offsetHeight") + height_offset
                    logging.info(f"Get {url} height: {height}")
                    browser_page.set_viewport_size({"width": width, "height": height})

                    # 重新进入页面
                    browser_page.goto(url)
                    browser_page.wait_for_load_state('networkidle')

                except Exception as e:
                    logging.warning(f"Failed to auto get {url} height: {str(e)}. Using default height.")

            elif auto_height and "viewPanel" in url:
                logging.warning(f"Panel page can't auto get {url} height. Using default height.")

            else:
                pass

            if hide_class is None:
                # .css-k3l5qq  v11.3.1 筛选器栏
                # .css-i7txp7  v11.3.1 提示条
                hide_class = [".css-i7txp7"]

            non_display = ", ".join(hide_class) + " {display: none !important;}"

            page_title = browser_page.title()
            screenshot:bytes = browser_page.screenshot(type=filetype, style=non_display)

            browser.close()
        return page_title, screenshot

    def panel_data_csv_(self, url, download_dir = "./"):
        if "viewPanel" not in url:
            raise ValueError("Not a Panel URL")

        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            browser_page = browser.new_page()
            browser_page.set_extra_http_headers(self._headers)
            browser_page.set_viewport_size({"width": 800, "height": 800})

            browser_page.goto(url)
            browser_page.wait_for_load_state('networkidle')

            logging.debug(browser_page.content())

            browser_page.keyboard.press('i')

            download_button = browser_page.locator("span:has-text('CSV')")
            expect(download_button).to_be_visible()
            with browser_page.expect_download() as download_info:
                download_button.click()

            download = download_info.value
            # 等待下载完成并保存文件
            download.save_as(f"{download_dir}/{download.suggested_filename}")
            logging.info(f"File downloaded: {download.suggested_filename}")
            browser.close()

        return f"{download_dir}/{download.suggested_filename}"


