from uploader.bilibiliuploader.bilibiliuploader import BilibiliUploader
from uploader.bilibiliuploader.core import VideoPart
from datetime import datetime, timedelta

import mysql.connector
from pathlib import Path

from utils import wechat

connection = mysql.connector.connect(
    host="localhost",  # 数据库主机
    user="root",  # 数据库用户名
    password="123456",  # 数据库密码
    database="xhs"  # 数据库名称
)
cursor = connection.cursor()


def upload_youtube_video(filepath, v_cover, title, video_h5_url, keywords, username, tid=228):
    # v_tag = keywords.split(",")
    uploader = BilibiliUploader()
    cookies_file = "C:/app/bilibili/cookies_" + username + ".json"
    uploader.login_by_access_token_file(cookies_file)
    aid, data = upload_f(uploader=uploader, video_path=filepath, v_title=title,
                         v_desc=title, v_cover=v_cover, v_tag=keywords, v_url=video_h5_url, tid=tid)
    if aid == 'error':
        print('上传失败:' + str(filepath) + ' : ' + str(data))
        return data
    else:
        print('上传成功:' + str(filepath))
        return 'success'


def upload_f(uploader, video_path=None, v_title=None, v_desc=None, v_cover=None,
             v_tag=None, v_url=None, tid=228):
    for i in range(len(v_tag)):
        if (len(v_tag[i]) > 19):
            v_tag[i] = v_tag[i][:19]
    if (len(v_tag) < 1):
        v_tag = ['美女']
    print(v_tag)
    if (len(v_title) >= 80):
        v_title = v_title[:80]
    # processing video file
    parts = []
    parts.append(VideoPart(
        path=video_path,
        title=v_title,
        desc=v_title
    ))
    '''
    parts.append(VideoPart(
        path="C:/Users/xxx/Videos/2.mp4",
        title="",
        desc=""
    ))
    '''

    # upload
    # copyright =2 move, =1 selfmade
    # tid = category
    return uploader.upload(
        parts=parts,
        copyright=1,
        title=v_title,
        tid=tid,
        tag=",".join(v_tag),
        desc=v_desc,
        # 转载必须填写来源
        # source=v_url,
        cover=v_cover,
        thread_pool_workers=1,
    )
    # tmp = [video_path, v_title, v_desc, ",".join(v_tag), v_url]
    # print(tmp)


def run():
    username = 'limin'
    cursor.execute(
        "SELECT	title,file_path,tags,a.id,bilibili_upcount,author_home,work_id,a.folder_path  FROM	videolist a	LEFT JOIN videodetails b ON a.link = b.link WHERE( bilibili_upcount is null or bilibili_upcount < 4) and is_download = 1")
    # 获取查询结果
    result = cursor.fetchall()
    for row in result:
        try:
            title = row[0]
            folder_path = row[7]
            # 设置要查询的文件夹路径
            folder_path = Path(folder_path)
            # 要查找的文件名
            file_name = row[6]
            # 查找文件
            file_path = next(folder_path.glob(f"{file_name}*"), None)
            upcount = row[4] or 0
            id = row[3]
            if file_path is None:
                # 更新数据库中上传计数为1
                cursor.execute("""
                                    UPDATE videolist
                                    SET  bilibili_upcount = %s
                                    WHERE id = %s
                                """, (upcount + 20, id))
                # 提交事务
                connection.commit()
                wechat.sendtext("title: [" + title + "] 上传成功")
                continue

            # 获取文件扩展名
            file_extension = file_path.suffix
            print(f"文件扩展名: {file_extension}")
            video_types = [
                '.mp4',
                '.mov'
            ]
            # 输入的标签列表
            tag = row[2]
            if tag is None:
                tag = ''
            tags = tag.split()
            author_home = row[5]
            # 使用列表推导式加上 # 前缀，并连接为一个字符串
            # formatted_tags = ' '.join([f"#{tag}" for tag in tags])
            # 判断文件是否为视频文件 不是则跳过
            if file_extension not in video_types:
                print(f"{file_path} 不是一个视频文件，类型为 {file_extension}")
                # 更新数据库中上传计数为1
                cursor.execute("""
                                    UPDATE videolist
                                    SET  bilibili_upcount = %s
                                    WHERE id = %s
                                """, (upcount + 10, id))
                # 提交事务
                connection.commit()
                wechat.sendtext("title: [" + title + "] 上传成功")
                continue
            # # 校验cookie是否过期
            # await tiktok_setup(tk_account_file, handle=True)
            # # 上传视频
            # app = TiktokVideo(title, file_path, tags, 0, tk_account_file, headless=False)
            # res = await app.main()
            res = upload_youtube_video(file_path, author_home, title + str(id), author_home, tags, username, 21)
            if res == 'success':
                # 更新数据库中上传计数为1
                cursor.execute("""
                                    UPDATE videolist
                                    SET  bilibili_upcount = %s
                                    WHERE id = %s
                                """, (upcount + 10, id))
                # 提交事务
                connection.commit()
                wechat.sendtext(f"小红书 to B站 [{username}]title: [{title}] 成功:{res}")
            else:
                # 更新数据库中上传计数为1
                cursor.execute("""
                                    UPDATE videolist
                                    SET  bilibili_upcount = %s
                                    WHERE id = %s
                                """, (upcount + 1, id))
                # 提交事务
                connection.commit()
                wechat.sendtext(f"小红书 to B站 [{username}]title: [{title}] 上传失败:{res}")
        except:
            upcount = row[4] or 0
            id = row[3]
            # 更新数据库中上传计数为1
            cursor.execute("""
                                    UPDATE videolist
                                    SET  bilibili_upcount = %s
                                    WHERE id = %s
                                """, (upcount + 30, id))
            wechat.sendtext(f"小红书 to B站 [{username}]id: [{id}] 上传失败!")


if __name__ == '__main__':
    run()
