# HNU_DailyClockin

## Usage

1. fork仓库

2. 在fork的仓库内的Settings->Secrets中添加如下条目

| secrets          | 说明           | 备注                                                   |
| ---------------- | -------------- | ------------------------------------------------------ |
| BAIDU_API_KEY    | 百度OCR API    |                                                        |
| BAIDU_SECRET_KEY | 百度OCR SECRET |                                                        |
| LOGIN_ID         | 打卡账号       |                                                        |
| LOGIN_PASSWORD   | 打卡密码       |                                                        |
| SERVERCHAN_SCKEY | Sever酱SCKEY   | 用于微信推送打卡通知，参考http://sc.ftqq.com/3.version |

3. 打开仓库的action
+ action触发机制
	+ push后自动触发 
	+ 在action中点击Run workflow
	+ 每日自动在00:15执行
		+ 时间修改：`.github/workflows/clockin.yml`中

```
  schedule:
 - cron: '15 16 * * *' #UTC时间，参考https://crontab.guru/
```
