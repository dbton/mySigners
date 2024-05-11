import requests,time,os
from lxml import etree

def main():
    # 判断是否已登陆
    print('检查是否已登陆')
    if not is_login():
        print('未登陆或cookie已失效')
        #raise Exception('invaild cookie,please update your cookie')
        check_error()
        exit()
    print('已登陆')

    task_url = 'https://i.pcbeta.com/home.php?mod=task'
    resp1 = requests.get(task_url,headers=headers,timeout=20)
    html = etree.HTML(resp1.text)
    task_list = html.xpath('//h3[@class="xs2 xi2"]/a/text()')
    if not task_list:
        print('未发现任务')
        exit()

    task_url_list = html.xpath('//h3[@class="xs2 xi2"]/a/@href')
    print(task_list,task_url_list)
    for i in task_url_list:
        id = i.split('&id=')[1]
        if id == '149':
            do_task_149()
        else:
            do_task_else(id)

def is_login():
    url = 'https://bbs.pcbeta.com/'
    resp = requests.get(url,headers=headers,timeout=20)
    html = etree.HTML(resp.text)
    user_name: list = html.xpath('//*[@id="um"]/div/strong/a/text()')
    return bool(user_name)

def check_error():
    url = 'https://bbs.pcbeta.com/'
    resp = requests.get(url,headers=headers,timeout=20)
    html = etree.HTML(resp.text)
    print(f'response_code:'{resp.status_code})
    print(html)

def do_task_149():
    print('开始执行任务149')
    time.sleep(2)
    print('申请任务')
    requests.get('https://i.pcbeta.com/home.php?mod=task&do=apply&id=149',headers=headers,timeout=20)
    time.sleep(2)
    print('执行')
    requests.get('https://i.pcbeta.com/home.php?mod=task&do=draw&id=149',headers=headers,timeout=20)
    print('task149执行成功',end=' ')

def do_task_else(id):
    print(f'开始执行任务{id}')
    time.sleep(0.5)
    print('申请任务')
    requests.get(f'https://i.pcbeta.com/home.php?mod=task&do=apply&id={id}',headers=headers,timeout=20)
    time.sleep(0.5)
    print('获取帖子链接')
    resp2 = requests.get(f'https://i.pcbeta.com/home.php?mod=task&do=view&id={id}',headers=headers,timeout=20)
    html = etree.HTML(resp2.text)
    url = html.xpath('//td[@class="bbda"]/a/@href')[0]
    tid = url.split('-')[1]
    resp3 = requests.get(url,headers=headers,timeout=20)
    formhash = etree.HTML(resp3.text).xpath('//form[@method="post"]/input[@name="formhash"]/@value')[0]
    post_url = f'https://bbs.pcbeta.com/forum.php?mod=post&infloat=yes&action=reply&fid=164&extra=&tid={tid}&replysubmit=yes&inajax=1'
    body = {
    'formhash': formhash,
    'handlekey': 'reply',
    'noticeauthor': '',
    'noticetrimstr': '',
    'noticeauthormsg': '',
    'subject': '',
    'message': '远景每日打卡专用'.encode('gbk')
    }
    print('post_url:',post_url)
    print('回帖')
    requests.post(post_url,headers=headers,data=body,timeout=20)
    print('执行')
    requests.get(f'https://i.pcbeta.com/home.php?mod=task&do=draw&id={id}',headers=headers,timeout=20)
    print(f'task{id}执行成功',end=' ')

if __name__ == '__main__':
    cookie = os.environ.get('YJ_COOKIE')
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': cookie,
    'pragma': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    }
    print('远景',end=':')
    main()