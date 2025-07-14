@echo off
echo [%date% %time%] Start Running >> C:\work\code\social-auto-upload\upload_log.txt
cd /d C:\work\code\social-auto-upload
"C:\Users\yu102\AppData\Local\Programs\Python\Python311\python.exe" xhs_to_tiktok_yuqi.py >> upload_output.txt 2>&1
echo [%date% %time%] Finished >> C:\work\code\social-auto-upload\upload_log.txt
