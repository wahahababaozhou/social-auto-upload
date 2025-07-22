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
            "SELECT	title,folder_path,work_id,tags,a.id,upcount FROM	videolist a	LEFT JOIN videodetails b ON a.link = b.link WHERE upcount = 0 and is_download = 1")
        # 获取查询结果
        result = self.cursor.fetchall()
        for row in result:
            try:
                self.cursor.execute("""
                SELECT last_upload_time FROM video_uploads WHERE id = %s
                """, ('yyy',))
                upload_time_row = self.cursor.fetchone()
                # 获取最后上传时间
                last_upload_time = upload_time_row[0] if upload_time_row else None
                # 检查最后上传时间是否在今天
                # if last_upload_time is not None and datetime.now() - last_upload_time < timedelta(hours=7):
                #     tiktok_logger.success("12小时内已经上传过视频了，跳过...")
                #     return
                tiktok_logger.success(row)
                title = row[0]
                tiktok_logger.success("tile:" + title)
                folder_path = row[1]
                tiktok_logger.success("filepath:" + folder_path)
                # 设置要查询的文件夹路径
                folder_path = Path(folder_path)
                # 要查找的文件名
                file_name = row[2]
                id = row[4]
                upcount = row[5]
                # 查找文件
                file_path = next(folder_path.glob(f"{file_name}*"), None)
                if file_path is None:
                    # 更新数据库中上传计数为1
                    self.cursor.execute("""
                                    UPDATE videolist
                                    SET  upcount = %s
                                    WHERE id = %s
                                """, (upcount + 1, id))
                    tiktok_logger.error("上传失败")
                    wechat.sendtext(f"小红书toTiktok,title: [{title}] 上传失败:未找对应ID{id}的视频文件！")
                    continue
                # 获取文件扩展名
                file_extension = file_path.suffix

                print(f"文件扩展名: {file_extension}")
                video_types = [
                    '.mp4',
                    '.mov'
                ]
                tag = row[3]
                if tag is None:
                    tag = ''
                # 输入的标签列表
                tags = tag.split()
                tiktok_logger.success("tags:" + row[3])

                # 使用列表推导式加上 # 前缀，并连接为一个字符串
                formatted_tags = ' '.join([f"#{tag}" for tag in tags])
                tiktok_logger.success("formatted_tags:" + formatted_tags)
                # 判断文件是否为视频文件 不是则跳过
                if file_extension not in video_types:
                    print(f"{file_path} 不是一个视频文件，类型为 {file_extension}")
                    tiktok_logger.success("非视频类,跳过成功")
                    # 更新数据库中上传计数为1
                    self.cursor.execute("""
                                    UPDATE videolist
                                    SET  upcount = %s
                                    WHERE id = %s
                                """, (upcount + 1, id))
                    # 提交事务
                    self.connection.commit()
                    wechat.sendtext("小红书toTiktok,title: [" + title + "] 上传成功")
                    continue
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
                    wechat.sendtext("小红书toTiktok,title: [" + title + "] 上传成功")
                else:
                    tiktok_logger.error("上传失败")
                    wechat.sendtext(f"小红书toTiktok,title: [{title}] 上传失败:{res}")
            except:
                tiktok_logger.error("上传失败")
                title = row[0]
                id = row[4]
                upcount = row[5]
                wechat.sendtext(f"上传至tiktok流程，title: [{title}] 上传失败!!!")
                # 更新数据库中上传计数为1
                self.cursor.execute("""
                                    UPDATE videolist
                                    SET  upcount = %s
                                    WHERE id = %s
                                """, (upcount + 1, id))

    async def start(self):
        try:
            await self.downloadxhsVideo()
        except Exception as e:
            tiktok_logger.error(e)
            wechat.sendtext("xhs to tiktok 执行失败1 downloadxhsVideo")
            wechat.sendtext(e)
        try:
            await self.uploadTiktokVideo()
        except Exception as e:
            tiktok_logger.error(e)
            wechat.sendtext("xhs to tiktok 执行失败2 uploadTiktokVideo")
            wechat.sendtext(e)
        finally:
            # 关闭数据库连接
            self.connection.close()
