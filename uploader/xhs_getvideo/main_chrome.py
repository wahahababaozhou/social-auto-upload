import os
from datetime import datetime

import mysql.connector
from playwright.async_api import Playwright, async_playwright

from conf import LOCAL_CHROME_PATH
from utils.base_social_media import set_init_script
from utils.files_times import get_absolute_path
from utils.log import tiktok_logger
from xhscore.source import XHS


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=account_file)
        context = await set_init_script(context)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://www.xiaohongshu.com/")
        await page.wait_for_load_state('load')
        try:
            # 选择所有的 select 元素
            user_elements = await page.query_selector_all('span[class="login-btn"]')
            if user_elements.__len__() != 0:
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
        self.page = None
        # 连接 MySQL 数据库
        self.connection = mysql.connector.connect(
            host="localhost",  # 数据库主机
            user="root",  # 数据库用户名
            password="123456",  # 数据库密码
            database="xhs"  # 数据库名称
        )
        self.cursor = self.connection.cursor()

    # 下载视频
    async def downloadVideo(self, link):
        """通过代码设置参数，适合二次开发"""
        # 示例链接
        # demo_link = "https://www.xiaohongshu.com/explore/675579fd000000000700eba7?xsec_token=ABf1BCGxU1gI7Q-w8wC3_IqdPRAgGXJRyEc8-fnJNGuhc=&xsec_source=pc_user"
        # 实例对象
        work_path = "D:\\xhs"  # 作品数据/文件保存根路径，默认值：项目根路径
        folder_name = "Download"  # 作品文件储存文件夹名称（自动创建），默认值：Download
        name_format = "作品ID"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"  # User-Agent
        cookie = ""  # 小红书网页版 Cookie，无需登录，可选参数，登录状态对数据采集有影响
        proxy = None  # 网络代理
        timeout = 5  # 请求数据超时限制，单位：秒，默认值：10
        chunk = 1024 * 1024 * 10  # 下载文件时，每次从服务器获取的数据块大小，单位：字节
        max_retry = 2  # 请求数据失败时，重试的最大次数，单位：秒，默认值：5
        record_data = False  # 是否保存作品数据至文件
        image_format = "WEBP"  # 图文作品文件下载格式，支持：PNG、WEBP
        folder_mode = False  # 是否将每个作品的文件储存至单独的文件夹
        async with XHS(
                work_path=work_path,
                folder_name=folder_name,
                name_format=name_format,
                user_agent=user_agent,
                cookie=cookie,
                proxy=proxy,
                timeout=timeout,
                chunk=chunk,
                max_retry=max_retry,
                record_data=record_data,
                image_format=image_format,
                folder_mode=folder_mode,
        ) as xhs:  # 使用自定义参数
            download = True  # 是否下载作品文件，默认值：False
            # 返回作品详细信息，包括下载地址
            # 获取数据失败时返回空字典
            # print(await xhs.extract(error_link, download, ))
            res = await xhs.extract(link, download, index=[1, 2])
            print(res)
            self.insertDetail(res[0])

    def insertDetail(self, item):
        # 检查 work_id 是否已存在
        check_query = "SELECT COUNT(*) FROM videodetails WHERE work_id = %s"
        # 检查 work_id 是否已经存在
        self.cursor.execute(check_query, (item['作品ID'],))
        count = self.cursor.fetchone()[0]

        if count != 0:
            # 如果已存在，可以选择跳过插入或进行更新
            print(f"work_id {item['作品ID']} 已存在，跳过插入。")
            return
        # 插入数据的 SQL 语句（使用英文字段名）
        insert_query = """
        INSERT INTO videodetails (
            collection_count, comment_count, share_count, like_count, tags, work_id, work_url, 
            title, description, work_type, publish_time, last_update_time, author_nickname, 
            author_id, author_url, download_url, gif_url, collection_time
        ) VALUES (
            %(collection_count)s, %(comment_count)s, %(share_count)s, %(like_count)s, %(tags)s, %(work_id)s, %(work_url)s, 
            %(title)s, %(description)s, %(work_type)s, %(publish_time)s, %(last_update_time)s, %(author_nickname)s, 
            %(author_id)s, %(author_url)s, %(download_url)s, %(gif_url)s, %(collection_time)s
        );
        """
        # 将中文字段名转换为英文
        data = {
            'collection_count': item.get('收藏数量', '') if item.get('收藏数量') else None,
            'comment_count': item.get('评论数量', '') if item.get('评论数量') else None,
            'share_count': item.get('分享数量', '') if item.get('分享数量') else None,
            'like_count': item.get('点赞数量', '') if item.get('点赞数量') else None,
            'tags': item.get('作品标签', '') if item.get('作品标签') else None,
            'work_id': item.get('作品ID', '') if item.get('作品ID') else None,
            'work_url': item.get('作品链接', '') if item.get('作品链接') else None,
            'title': item.get('作品标题', '') if item.get('作品标题') else None,
            'description': item.get('作品描述', '') if item.get('作品描述') else None,
            'work_type': item.get('作品类型', '') if item.get('作品类型') else None,
            'publish_time': datetime.strptime(item.get('发布时间', '1970-01-01_00:00:00'),
                                              '%Y-%m-%d_%H:%M:%S') if item.get('发布时间') else None,
            'last_update_time': datetime.strptime(item.get('最后更新时间', '1970-01-01_00:00:00'),
                                                  '%Y-%m-%d_%H:%M:%S') if item.get('最后更新时间') else None,
            'author_nickname': item.get('作者昵称', '') if item.get('作者昵称') else None,
            'author_id': item.get('作者ID', '') if item.get('作者ID') else None,
            'author_url': item.get('作者链接', '') if item.get('作者链接') else None,
            'download_url': ','.join(item.get('下载地址', [])) if item.get('下载地址') else None,  # 合并下载地址列表
            'gif_url': ','.join(str(url) for url in item.get('动图地址', []) if url) if item.get('动图地址') else None,
            'collection_time': datetime.strptime(item.get('采集时间', '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
            if item.get('采集时间') else None
        }

        # 插入数据
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    # 向mysql插入数据的函数
    async def insert_data(self, link, author, author_home, find_data, is_download, file_path):
        try:
            # 检查 link 是否已存在
            self.cursor.execute("SELECT COUNT(*) FROM videolist WHERE link = %s", (link,))
            count = self.cursor.fetchone()[0]

            if count > 0:
                print(f"链接 {link} 已存在，跳过插入")
            else:
                # 执行插入操作
                self.cursor.execute("""
                    INSERT INTO videolist (link, author, author_home, find_data, is_download, file_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (link, author, author_home, find_data, is_download, file_path))
                self.connection.commit()
                print(f"成功插入数据: {link}")

        except mysql.connector.Error as err:
            print(f"插入数据时发生错误: {err}")
        finally:
            # 不在每次调用时关闭连接，保持连接池更高效。
            pass

    async def getVideoDownloadedURL(self, url):
        # 获取所有符合条件的 a 标签
        elements = await self.page.query_selector_all('a[href="' + url + '"]')
        # 如果找到了元素，点击第一个元素（或者根据需要选择特定的元素）
        if elements:
            # 这里选择点击第一个元素
            parent_element = await elements[0].evaluate_handle('(element) => element.parentElement')
            # 点击父级元素
            await parent_element.click()

            await self.page.wait_for_load_state('load')
            # 获取跳转后的页面 URL
            current_url = self.page.url
            print(current_url)
            # 回退到上一个页面
            await self.page.go_back()
            # 等待回退后的页面加载完成
            await self.page.wait_for_load_state('load')
            await self.page.wait_for_timeout(5000)  # 加载完成后再等待5秒
            return current_url
        else:
            print("current_url get error")
            return None

    async def getUserHome(self, playwright: Playwright):
        browser = await playwright.chromium.launch(headless=False, executable_path=self.local_executable_path)
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)
        self.page = await context.new_page()
        # 访问用户主页
        await self.page.goto(self.url)  # 替换为目标用户主页链接
        # 等待页面加载
        await self.page.wait_for_selector('div.user-name')  # 替换为你需要的元素
        # 等待页面加载完成
        # await page.wait_for_selector('a[style="display:none;"]')

        # 使用 JavaScript 获取所有符合条件的 a 标签
        elements = await self.page.query_selector_all('a[href*="/explore/"]')
        # 获取元素的相关信息，如 href 和其他属性
        links = []
        for element in elements:
            href = await element.get_attribute('href')
            links.append(href)
        # 打印所有符合条件的 a 标签的 href
        for link in links:
            print(link)
            # 检查 link 是否已存在
            # self.cursor.execute("SELECT * FROM videolist WHERE link = %s", (link,))
            self.cursor.execute(
                "SELECT link, author, author_home, find_data, is_download, file_path,id FROM videolist WHERE link = %s",
                (link,))
            # 获取查询结果
            result = self.cursor.fetchone()
            if result:
                # 提取字段值
                link_from_db = result[0]
                author_from_db = result[1]
                author_home_from_db = result[2]
                find_data_from_db = result[3]
                is_download_from_db = result[4]
                file_path_from_db = result[5]
                id = result[6]
                # 打印或返回查询的结果
                print(f"ID: {id}")
                print(f"链接: {link_from_db}")
                print(f"作者: {author_from_db}")
                print(f"作者首页URL: {author_home_from_db}")
                print(f"爬取时间: {find_data_from_db}")
                print(f"是否下载: {is_download_from_db}")
                print(f"文件路径: {file_path_from_db}")
                # 检查是否下载
                if is_download_from_db == '0':
                    # 获取视频下载URL
                    downloadUrl = await self.getVideoDownloadedURL(link)
                    if downloadUrl is None:
                        continue
                    # 下载视频
                    await self.downloadVideo(downloadUrl)
                    # 更新数据库中 is_download 字段为 1
                    self.cursor.execute("""
                            UPDATE videolist
                            SET  is_download = %s
                            WHERE id = %s
                        """, ('1', id))
                    # 提交事务
                    self.connection.commit()
            else:
                print("新视频，准备下载并插入记录......")
                # 获取视频下载URL
                downloadUrl = await self.getVideoDownloadedURL(link)
                if downloadUrl is None:
                    continue
                # 下载视频
                await self.downloadVideo(downloadUrl)
                # 插入记录
                await self.insert_data(
                    link,
                    self.author,
                    self.url,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    True,
                    ""
                )
        # 关闭浏览器
        await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.getUserHome(playwright)
