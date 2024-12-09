import asyncio
from pathlib import Path

from conf import BASE_DIR
# from tk_uploader.main import tiktok_setup, TiktokVideo
from uploader.xhs_getvideo.main_chrome import xhsVideo, xhs_setup

if __name__ == '__main__':
    account_file = Path(BASE_DIR / "cookies" / "xhs_uploader" / "account.json")
    url = 'https://www.xiaohongshu.com/user/profile/5b6568aa11be106304b4473f?xsec_token=&xsec_source=pc_note'
    # get video files from folder
    cookie_setup = asyncio.run(xhs_setup(account_file, handle=False))
    app = xhsVideo(account_file, url, '笨蛋土豆丝')
    asyncio.run(app.main(), debug=True)
