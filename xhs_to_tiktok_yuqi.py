import asyncio
from pathlib import Path

from conf import BASE_DIR
from xhs2tiktok.main import xhs2tiktok

if __name__ == '__main__':
    xhs_account_file = Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json")
    tk_account_file = Path(BASE_DIR / "cookies" / "tk_uploader" / "account.json")
    url = 'https://www.xiaohongshu.com/user/profile/5b6568aa11be106304b4473f?xsec_token=&xsec_source=pc_note'
    author = '笨蛋土豆丝'
    app = xhs2tiktok(xhs_account_file, tk_account_file, url, author)
    asyncio.run(app.start(), debug=False)
