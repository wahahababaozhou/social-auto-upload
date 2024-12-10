import mysql.connector

from uploader.tk_uploader.main_chrome import tiktok_setup, TiktokVideo
from uploader.xhs_getvideo.main_chrome import xhsVideo, xhs_setup


class xhs2tiktok(object):
    def __init__(self, xhs_account_file, tk_account_file, url, author):
        self.xhs_account_file = xhs_account_file
        self.tk_account_file = tk_account_file
        self.url = url
        self.author = author
        # 连接 MySQL 数据库
        self.connection = mysql.connector.connect(
            host="localhost",  # 数据库主机
            user="root",  # 数据库用户名
            password="123456",  # 数据库密码
            database="xhs"  # 数据库名称
        )
        self.cursor = self.connection.cursor()

    # 下载视频
    async def downloadxhsVideo(self):
        # 校验是否登录
        await xhs_setup(self.xhs_account_file, handle=False)
        # 获取视频
        app = xhsVideo(self.xhs_account_file, self.url, self.author)
        await app.main()

    async def uploadTiktokVideo(self):
        self.cursor.execute(
            "SELECT	* FROM	videolist a	LEFT JOIN videodetails b ON a.link = b.link WHERE	upcount = 0")
        # 获取查询结果
        result = self.cursor.fetchall()
        for row in result:
            print(row)
            title = row[16]
            print("tile:" + title)
            filepath = row[27]
            print("filepath:" + filepath)
            # 输入的标签列表
            tags = row[13].split()
            print("tags:" + row[13])
            id = row[6]
            upcount = row[7]
            # 使用列表推导式加上 # 前缀，并连接为一个字符串
            formatted_tags = ' '.join([f"#{tag}" for tag in tags])
            print("formatted_tags:" + formatted_tags)
            # 校验cookie是否过期
            await tiktok_setup(self.tk_account_file, handle=True)
            # 上传视频
            app = TiktokVideo(title, filepath, tags, 0, self.tk_account_file)
            await app.main()
            # 更新数据库中上传计数为1
            self.cursor.execute("""
                            UPDATE videolist
                            SET  upcount = %s
                            WHERE id = %s
                        """, (upcount + 1, id))
            # 提交事务
            self.connection.commit()

    async def start(self):
        await self.downloadxhsVideo()
        await self.uploadTiktokVideo()
