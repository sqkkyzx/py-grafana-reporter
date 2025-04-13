import logging
from typing import Literal

from playwright.sync_api import sync_playwright
import httpx


class GrafanaRender:
    def __init__(self, base_url:str, token: str, browser: Literal["chromium", "firefox"] = "firefox", remote_browser_ws: str = "", remote_browser_cdp: str = ""):
        self.base_url = base_url.rstrip('/')
        self.token:str = token
        self.browser_type = browser
        self.remote_browser_ws = remote_browser_ws
        self.remote_browser_cdp = remote_browser_cdp

        self._headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange",
            "cache-control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            'Authorization': f'Bearer {self.token}'
        }

        if not self.remote_browser_ws and not self.remote_browser_cdp:
            raise "remote_browser_ws 或 remote_browser_cdp 至少提供一个"


    def snapshot(self, url: str = "", uid = "", query_string = None, width:int=762, height:int=300, auto_height=True,
                 auto_height_offset:int=150, hide_class:list = None, data_load_timeout = 5000,
                 filetype: Literal["jpeg", "png"]= "png", file_path:str = None) -> (str, bytes):
        """

        :param uid: 仪表盘 UID
        :param query_string: 查询参数字符串，必须以 ? 开头
        :param url: 截图页面
        :param width: 截图宽度
        :param height: 截图高度
        :param auto_height: 自动获取实际高度
        :param auto_height_offset: 高度偏移
        :param data_load_timeout: 页面加载完成后，等待数据加载的时间
        :param hide_class: 隐藏的样式选择器列表， 比如 .css-k3l5qq 是 v11.3.1 的顶部筛选器栏
        :param filetype: 截图格式，可选择 png 或 jpeg
        :param file_path: 截图文件保存路径，需要包括文件名的完整路径。可以不传入，获取截图字节流后自行保存。
        :return:
            - page_title: 页面标题
            - screenshot: 截图的字节流
        """
        if not url:
            if not uid:
                raise "必须提供 url 参数 或 uid 参数"
            if not self.base_url:
                raise "使用 uid 参数时，必须提供 base_url"
            if query_string and query_string[0] != "?":
                query_string = "?" + query_string

            url = self.base_url + self.get_dashboard_info(uid).get("meta").get("url") + query_string

        with sync_playwright() as playwright:
            if self.remote_browser_ws:
                browser = playwright[self.browser_type].connect(self.remote_browser_ws)
            else:
                browser = playwright[self.browser_type].launch(headless=True)

            browser_page = browser.new_page()
            browser_page.set_extra_http_headers(self._headers)
            browser_page.set_viewport_size({"width": width, "height": height})

            try:
                browser_page.goto(url)
                browser_page.wait_for_selector(selector=".react-grid-layout",state="attached", timeout=60000)

                if auto_height and "viewPanel" not in url:
                    try:
                        # 获取到 .react-grid-layout 的高度并加上一定偏移作为真实高度，然后重新设置窗口大小
                        height = browser_page.evaluate("document.querySelector('.react-grid-layout').offsetHeight") + auto_height_offset
                        logging.info(f"Get {url} height: {height}")
                        browser_page.set_viewport_size({"width": width, "height": height})

                        # 重新进入页面
                        browser_page.goto(url)
                        browser_page.wait_for_selector(selector=".react-grid-layout", state="attached", timeout=60000)
                        browser_page.wait_for_selector(selector=".react-grid-item", state="attached", timeout=60000)
                        # 等待数据加载
                        browser_page.wait_for_timeout(data_load_timeout)

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

                non_display_class = ", ".join(hide_class) + " {display: none !important;}"
                screenshot:bytes = browser_page.screenshot(type=filetype, style=non_display_class, path=file_path)
                return screenshot
            except Exception as e:
                logging.error(e)
                raise
            finally:
                browser.close()

    def get_dashboard_info(self, uid:str) -> dict:
        if not self.base_url:
            raise "必须提供 base_url"
        url =  f'{self.base_url}/api/dashboards/uid/{uid}'
        print(url)
        headers = self._headers
        headers["Accept"] = "application/json"
        res = httpx.get(url, headers=self._headers, timeout=15)
        print(res)
        return res.json()