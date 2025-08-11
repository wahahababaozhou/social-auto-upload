import asyncio
from pathlib import Path

import xhs_to_bilibili_limin
from conf import BASE_DIR
from xhs2tiktok.main import xhs2tiktok

if __name__ == '__main__':
    tk_account_file = Path(BASE_DIR / "cookies" / "tk_uploader" / "account.json")
    xhs_config = [
        # {
        #     "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
        #     "url": 'https://www.xiaohongshu.com/user/profile/5b6568aa11be106304b4473f?xsec_token=&xsec_source=pc_note',
        #     "author": '笨蛋土豆丝'
        # },
        # {
        #     "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
        #     "url": 'https://www.xiaohongshu.com/user/profile/65929d3a0000000022006f3c?xsec_token=&xsec_source=pc_note',
        #     "author": "甜菜大王o"
        # },
        # {
        #     "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
        #     "url": 'https://www.xiaohongshu.com/user/profile/63df231d0000000026004748?xsec_token=&xsec_source=pc_note',
        #     "author": "纯情美女总犯困"
        # }
        {
            "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
            "url": 'https://www.xiaohongshu.com/user/profile/65a0d4820000000022002ad1?xsec_token=&xsec_source=pc_note',
            "author": "乐亦"
        },
        {
            "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
            "url": 'https://www.xiaohongshu.com/user/profile/620760c800000000100059d7?xsec_token=&xsec_source=pc_note',
            "author": "ing"
        },
        {
            "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
            "url": 'https://www.xiaohongshu.com/user/profile/65394ed60000000006004a1a?xsec_token=&xsec_source=pc_note',
            "author": "小李财"
        }
        # ,
        # {
        #     "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
        #     "url": 'https://www.xiaohongshu.com/user/profile/5a8ba77211be102527e3e730?xsec_token=&xsec_source=pc_note',
        #     "author": "小羊同学"
        # }
    ]
    app = xhs2tiktok(xhs_config, tk_account_file)
    asyncio.run(app.start(), debug=False)
    # 小红书视频搬运到B站limin账号下
    # xhs_to_bilibili_limin.run()
