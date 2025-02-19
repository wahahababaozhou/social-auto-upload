import asyncio
from pathlib import Path

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
        {
            "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
            "url": 'https://www.xiaohongshu.com/user/profile/65929d3a0000000022006f3c?xsec_token=&xsec_source=pc_note',
            "author": "甜菜大王o"
        },
        # {
        #     "xhs_account_file": Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json"),
        #     "url": 'https://www.xiaohongshu.com/user/profile/63df231d0000000026004748?xsec_token=&xsec_source=pc_note',
        #     "author": "纯情美女总犯困"
        # }
    ]
    app = xhs2tiktok(xhs_config, tk_account_file)
    asyncio.run(app.start(), debug=False)
