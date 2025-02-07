import logging
import re
from typing import Literal

from playwright.sync_api import sync_playwright


class GrafanaRender:
    def __init__(self, token: str, browser: Literal["chromium", "firefox"] = "firefox", remote_browser_ws: str = ""):
        self.token:str = token
        self.browser_type = browser
        self.remote_browser_ws = remote_browser_ws

        self._headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange",
            "cache-control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            'Authorization': f'Bearer {self.token}'
        }

    def snapshot(self, url: str, width:int=762, height:int=300, auto_height=True,
                 auto_height_offset:int=150, hide_class:list = None,
                 filetype: Literal["jpeg", "png"]= "png", file_path:str = None) -> (str, bytes):
        """

        :param url: 截图页面
        :param width: 截图宽度
        :param height: 截图高度
        :param auto_height: 自动获取实际高度
        :param auto_height_offset: 高度偏移
        :param hide_class: 隐藏的样式选择器列表， 比如 .css-k3l5qq 是 v11.3.1 的顶部筛选器栏
        :param filetype: 截图格式，可选择 png 或 jpeg
        :param file_path: 截图文件保存路径，需要包括文件名的完整路径。可以不传入，获取截图字节流后自行保存。
        :return:
            - page_title: 页面标题
            - screenshot: 截图的字节流
        """
        with sync_playwright() as playwright:
            if self.remote_browser_ws:
                browser = playwright[self.browser_type].connect(self.remote_browser_ws)
            else:
                browser = playwright[self.browser_type].launch(headless=True)

            browser_page = browser.new_page()
            browser_page.set_extra_http_headers(self._headers)
            browser_page.set_viewport_size({"width": width, "height": height})

            browser_page.goto(url)
            browser_page.wait_for_load_state('networkidle')

            logging.debug(browser_page.content())

            if auto_height and "viewPanel" not in url:
                try:
                    # 获取到 .react-grid-layout 的高度并加上一定偏移作为真实高度，然后重新设置窗口大小
                    height = browser_page.evaluate("document.querySelector('.react-grid-layout').offsetHeight") + auto_height_offset
                    logging.info(f"Get {url} height: {height}")
                    browser_page.set_viewport_size({"width": width, "height": height})

                    # 重新进入页面
                    browser_page.goto(url)
                    browser_page.wait_for_load_state('networkidle')

                except Exception as e:
                    logging.warning(f"Failed to auto get {url} height: {str(e)}. Using default height.")

            elif auto_height and "viewPanel" in url:
                    logging.warning(f"Cannot to auto get {url} height. Using default height.")
            else:
                pass

            if hide_class is None:
                # .css-k3l5qq  v11.3.1 筛选器栏
                # .css-i7txp7  v11.3.1 提示条
                hide_class = [".css-i7txp7"]

            non_display = ", ".join(hide_class) + " {display: none !important;}"

            page_title = browser_page.title()

            screenshot:bytes = browser_page.screenshot(type=filetype, style=non_display, path=file_path)

            browser.close()
        return page_title, screenshot
