import asyncio
import time
from package import dm, send_message

"""
需要 aiohttp 模块进行 WebSocket 连接
弹幕数据解析参考了 https://github.com/xfgryujk/blivedm 的代码

room_list
    type: list
    直播间id，整数型

提醒方式：
    1. Telegram
    2. Server酱（通过微信提醒）【http://sc.ftqq.com/3.version】

  Telegram：
    tg: 启用则 True，否则 False
    tg_token: 你的 Bot 的 token
    tg_id: 你的tg账号的 id

  Server酱：
    sc: 启用则 True，否则 False
    sc_token: 你的 SCKEY
"""


room_list = [  # 房间ID，每个ID用 英文逗号 隔开
    21615277,
    21756924,
    22300771
]

tg = False  # 是否使用 Telegram 通知
sc = True  # 是否使用 Server酱 通知
tg_token = ''  # Telegram机器人 的 Token
tg_id = ''  # Telegram账号 的 ID
sc_token = 'SCT58811TgHZjFDgG2y6XRKEIOD9GVhkJ'  # Server酱 的 Token

ssl = None  # SSL

room_result = {}
tasks = []


async def get_message(queue):
    s_m = send_message.SessionAio(tg_token=tg_token, tg_id=tg_id, sc_token=sc_token, loop=loop)
    while True:
        data = await queue.get()
        print(data)
        if (data['live_status'] == 'LIVE' and room_result[data['room_id']] is True) or \
                (data['live_status'] == 'PREPARING' and room_result[data['room_id']] is False):
            continue
        if data['live_status'] == 'LIVE':
            room_result[data['room_id']] = True
        else:
            room_result[data['room_id']] = False
            continue
        text = '【%s】%s\n%s' % (data['name'], '开播啦' if data['live_status'] == 'LIVE' else '下播啦',
                               time.strftime(u'%Y年%m月%d日 %H:%M:%S'.encode('unicode_escape').decode('utf8'),
                                             time.localtime()).encode('utf-8').decode('unicode_escape'))
        title = '【%s】%s' % (data['name'], '开播啦' if data['live_status'] == 'LIVE' else '下播啦')
        await s_m.send(tg=tg, sc=sc, sc_title=title, text=text)


if __name__ == '__main__':
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    for room_id in room_list:
        room_result[room_id] = False
        task = asyncio.ensure_future(dm.DM(room_id=room_id, loop=loop, queue=q, ssl=ssl).run())
        tasks.append(task)
    tasks.append(asyncio.ensure_future(get_message(queue=q)))
    loop.run_until_complete(asyncio.wait(tasks))
