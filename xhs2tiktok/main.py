from datetime import datetime, timedelta

import mysql.connector

from uploader.tk_uploader.main_chrome import tiktok_setup, TiktokVideo
from uploader.xhs_getvideo.main_chrome import xhsVideo, xhs_setup
from pathlib import Path

from utils import wechat
from utils.log import tiktok_logger


class xhs2tiktok(object):
    def __init__(self, xhs_config, tk_account_file):
        self.tk_account_file = tk_account_file
        self.xhs_config = xhs_config
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
        for config in self.xhs_config:
            # 校验是否登录
            await xhs_setup(config["xhs_account_file"], handle=False)
            # 获取视频
            app = xhsVideo(config["xhs_account_file"], config["url"], config["author"])
            await app.main()

    async def uploadTiktokVideo(self):
        self.cursor.execute(
            "SELECT	* FROM	videolist a	LEFT JOIN videodetails b ON a.link = b.link WHERE	upcount = 0")
        # 获取查询结果
        result = self.cursor.fetchall()
        for row in result:
            self.cursor.execute("""
            SELECT last_upload_time FROM video_uploads WHERE id = %s
            """, ('yyy',))
            upload_time_row = self.cursor.fetchone()
            # 获取最后上传时间
            last_upload_time = upload_time_row[0] if upload_time_row else None
            # 检查最后上传时间是否在今天
            if last_upload_time is not None and datetime.now() - last_upload_time < timedelta(hours=12):
                tiktok_logger.success("12小时内已经上传过视频了，跳过...")
                return
            tiktok_logger.success(row)
            title = row[16]
            tiktok_logger.success("tile:" + title)
            folder_path = row[5]
            tiktok_logger.success("filepath:" + folder_path)
            # 设置要查询的文件夹路径
            folder_path = Path(folder_path)
            # 要查找的文件名
            file_name = row[14]
            # 查找文件
            file_path = next(folder_path.glob(f"{file_name}*"), None)
            # 输入的标签列表
            tags = row[13].split()
            tiktok_logger.success("tags:" + row[13])
            id = row[6]
            upcount = row[7]
            # 使用列表推导式加上 # 前缀，并连接为一个字符串
            formatted_tags = ' '.join([f"#{tag}" for tag in tags])
            tiktok_logger.success("formatted_tags:" + formatted_tags)
            # 校验cookie是否过期
            await tiktok_setup(self.tk_account_file, handle=True)
            # 上传视频
            app = TiktokVideo(title, file_path, tags, 0, self.tk_account_file, headless=False)
            res = await app.main()
            if res == 'success':
                tiktok_logger.success("上传成功")
                # 更新数据库中上传计数为1
                self.cursor.execute("""
                                UPDATE videolist
                                SET  upcount = %s
                                WHERE id = %s
                            """, (upcount + 1, id))
                # 更新 last_upload_time
                self.cursor.execute("""
                    UPDATE video_uploads set last_upload_time=%s where id=%s
                """, (datetime.now(), "yyy"))
                # 提交事务
                self.connection.commit()
                wechat.sendtext("title: [" + title + "] 上传成功")
            else:
                tiktok_logger.error("上传失败")
                wechat.sendtext(f"title: [{title}] 上传失败:{res}")

    async def start(self):
        try:
            await self.downloadxhsVideo()
            await self.uploadTiktokVideo()
        except Exception as e:
            tiktok_logger.error(e)
            wechat.sendtext("tiktok to xhs 执行失败")
            wechat.sendtext(e)
        finally:
            # 关闭数据库连接
            self.connection.close()
