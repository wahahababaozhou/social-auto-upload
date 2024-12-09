import os
from datetime import datetime

import mysql.connector
from playwright.async_api import Playwright, async_playwright

from conf import LOCAL_CHROME_PATH
from utils.base_social_media import set_init_script
from utils.files_times import get_absolute_path
from utils.log import tiktok_logger

# 连接 MySQL 数据库
connection = mysql.connector.connect(
    host="localhost",  # 数据库主机
    user="root",  # 数据库用户名
    password="123456",  # 数据库密码
    database="xhs"  # 数据库名称
)

# 连接 MySQL 数据库
connection = mysql.connector.connect(
    host="localhost",  # 数据库主机
    user="root",  # 数据库用户名
    password="123456",  # 数据库密码
    database="xhs"  # 数据库名称
)
cursor = connection.cursor()

# 插入数据的函数
def insert_data(link, author, author_home, find_data, is_download, file_path):
    try:
        # 检查 link 是否已存在
        cursor.execute("SELECT COUNT(*) FROM videolist WHERE link = %s", (link,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"链接 {link} 已存在，跳过插入")
        else:
            # 执行插入操作
            cursor.execute("""
                INSERT INTO videolist (link, author, author_home, find_data, is_download, file_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (link, author, author_home, find_data, is_download, file_path))
            connection.commit()
            print(f"成功插入数据: {link}")

    except mysql.connector.Error as err:
        print(f"插入数据时发生错误: {err}")
    finally:
        # 不在每次调用时关闭连接，保持连接池更高效。
        pass


# 使用示例
# insert_data(
#     "https://example.com/video123",
#     "作者名字",
#     "https://example.com/author123",
#     "2024-12-09 10:00:00",
#     True,
#     "/path/to/file"
# )


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=account_file)
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://www.xiaohongshu.com/")
        await page.wait_for_load_state('load')
        try:
            # 选择所有的 select 元素
            user_elements = await page.query_selector_all('a[href*="user/profile/"]')
            if user_elements.__len__() == 0:
                tiktok_logger.error("[+] cookie expired")
                return False
            tiktok_logger.success("[+] cookie valid")
            return True
        except:
            tiktok_logger.success("[+] cookie valid")
            return True


async def get_xhs_cookie(account_file):
    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang zh-CN',
            ],
            'headless': False,  # Set headless option here
        }
        # Make sure to run headed.
        browser = await playwright.chromium.launch(**options)
        # Setup context however you like.
        context = await browser.new_context()  # Pass any options
        context = await set_init_script(context)
        # Pause the page, and start recording manually.
        page = await context.new_page()
        await page.goto("https://www.xiaohongshu.com/explore")
        await page.pause()
        # 点击调试器的继续，保存cookie
        await context.storage_state(path=account_file)


async def xhs_setup(account_file, handle=False):
    account_file = get_absolute_path(account_file, "xhs_uploader")
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return False
        tiktok_logger.info(
            '[+] cookie file is not existed or expired. Now open the browser auto. Please login with your way(gmail phone, whatever, the cookie file will generated after login')
        await get_xhs_cookie(account_file)
    return True


class xhsVideo(object):
    def __init__(self, account_file, url, author):
        self.account_file = account_file
        self.url = url
        self.author = author
        self.local_executable_path = LOCAL_CHROME_PATH
        self.locator_base = None

    async def getUserHome(self, playwright: Playwright):
        browser = await playwright.chromium.launch(headless=False, executable_path=self.local_executable_path)
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)
        page = await context.new_page()
        # 访问用户主页
        await page.goto(self.url)  # 替换为目标用户主页链接
        # 等待页面加载
        await page.wait_for_selector('div.user-name')  # 替换为你需要的元素
        # 等待页面加载完成
        # await page.wait_for_selector('a[style="display:none;"]')

        # 使用 JavaScript 获取所有符合条件的 a 标签
        elements = await page.query_selector_all('a[href*="/explore/"]')
        # 获取元素的相关信息，如 href 和其他属性
        links = []
        for element in elements:
            href = await element.get_attribute('href')
            links.append(href)
        # 打印所有符合条件的 a 标签的 href
        for link in links:
            print(link)
            insert_data(
                link,
                self.author,
                self.url,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                False,
                ""
            )
        # 关闭浏览器
        await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.getUserHome(playwright)
