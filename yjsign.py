import requests
import time
import os
import logging
from lxml import etree
import telepot

# 配置与常量
COOKIE: str = os.environ.get('YJ_COOKIE', '')
telekey: str = os.environ.get('YJ_TELEKEY', '')
teleid: str = os.environ.get('YJ_TELEID', '')
MSG: str = '远景论坛签到任务：\n'
TASK_BASE_URL = 'https://i.pcbeta.com/home.php?mod=task'
FORUM_BASE_URL = 'https://bbs.pcbeta.com/forum.php'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': COOKIE,
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

# 辅助函数
def send_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, headers=HEADERS, timeout=20, **kwargs)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None

def parse_html(response, xpath_expr):
    if not response:
        return []
    html = etree.HTML(response.text)
    return html.xpath(xpath_expr)

# 核心功能
def is_logged_in():
    home_url = 'https://bbs.pcbeta.com/'
    response = send_request('get', home_url)
    user_name = parse_html(response, '//*[@id="um"]/div/strong/a/text()')
    return bool(user_name)

def get_task_list():
    response = send_request('get', TASK_BASE_URL)
    task_titles = parse_html(response, '//h3[@class="xs2 xi2"]/a/text()')
    task_links = parse_html(response, '//h3[@class="xs2 xi2"]/a/@href')
    return task_titles, task_links

def apply_task(task_id):
    """
    申请任务
    """
    logging.info(f'申请任务 {task_id}')
    response = send_request('get', f'{TASK_BASE_URL}&do=apply&id={task_id}')
    if not response:
        logging.error(f'任务 {task_id} 申请失败')
        return False
    (f'任务 {task_id} 申请成功')
    return True

def draw_task_reward(task_id):
    """
    领取任务奖励
    """
    (f'领取任务 {task_id} 的奖励')
    response = send_request('get', f'{TASK_BASE_URL}&do=draw&id={task_id}')
    if not response:
        logging.error(f'任务 {task_id} 奖励领取失败')
        return False
    (f'任务 {task_id} 奖励领取成功')
    return True

def apply_and_draw_task(task_id):
    """
    申请并领取任务奖励
    """
    if apply_task(task_id):
        time.sleep(1)
        draw_task_reward(task_id)

def handle_task_with_post(task_id):
    """
    处理需要回帖的任务
    """
    (f'处理需要回帖的任务 {task_id}')
    if not apply_task(task_id):
        return
    response = send_request('get', f'{TASK_BASE_URL}&do=view&id={task_id}')
    post_link = parse_html(response, '//td[@class="bbda"]/a/@href')[0]
    if 'viewthread' not in post_link:
        logging.error('帖子链接格式错误')
        return
    thread_id = post_link.split('-')[1]
    post_response = send_request('get', post_link)
    formhash = parse_html(post_response, '//form[@method="post"]/input[@name="formhash"]/@value')[0]
    reply_url = f'{FORUM_BASE_URL}?mod=post&infloat=yes&action=reply&fid=164&extra=&tid={thread_id}&replysubmit=yes&inajax=1'
    reply_data = {
        'formhash': formhash,
        'handlekey': 'reply',
        'noticeauthor': '',
        'noticetrimstr': '',
        'noticeauthormsg': '',
        'usesig': '1',
        'subject': '',
        'message': '远景每日打卡专用'
    }
    response = send_request('post', reply_url, data=reply_data)
    if response and '回复发布成功' in response.text:
        ('回帖成功')
    draw_task_reward(task_id)


def process_tasks():
    """
    处理所有任务并比较任务列表
    """
    global MSG
    initial_task_titles, task_links = get_task_list()
    if not initial_task_titles:
        ('未发现任务')
        MSG += '未发现任务\n'
        return
    (f'发现任务: {initial_task_titles}')
    MSG += f'发现任务: {initial_task_titles}\n'
    for task_link in task_links:
        task_id = task_link.split('&id=')[1]
        if task_id == '149':
            apply_and_draw_task(task_id)
        else:
            handle_task_with_post(task_id)
    
    # 添加延时以确保任务状态更新
    time.sleep(5)
    
    # 重新获取任务列表
    confirm_task_completion()

def confirm_task_completion():
    global MSG
    task_doing_url = f'{TASK_BASE_URL}&item=doing'
    response = send_request('get', task_doing_url)
    ongoing_tasks = parse_html(response, '//h3[@class="xs2 xi2"]/a/text()')
    if ongoing_tasks:
        (f'进行中的任务: {ongoing_tasks}')
        MSG += f'进行中的任务: {ongoing_tasks}\n'
    else:
        ('没有进行中的任务，所有任务已完成')
        MSG += '没有进行中的任务，所有任务已完成\n'

# 获取 PB 币
def get_pb_coins():
    """
    获取 PB 币
    """
    pb_coins_url = 'https://i.pcbeta.com/home.php?mod=spacecp&ac=credit'
    response = send_request('get', pb_coins_url)
    pb_coins_text = parse_html(response, '//*[@id="ct"]/div[1]/div/ul[2]/li[1]/text()')
    if not pb_coins_text:
        logging.error('PB 币文本解析失败')
        return 0
    logging.debug(f'PB 币文本: {pb_coins_text}')
    pb_coins = pb_coins_text[1].strip()
    return pb_coins

def calculate_pb_coins_difference(start_coins, end_coins):
    """
    计算签到后获得的 PB 币
    """
    try:
        start = int(start_coins)
        end = int(end_coins)
        gained_coins = end - start
        (f'签到后获得的 PB 币: {gained_coins}')
        return gained_coins
    except ValueError:
        logging.error('PB 币计算失败，值无效')
        return 0

# 主函数
def main():
    global MSG
    if not COOKIE:
        logging.error('Cookie为空，请设置环境变量YJ_COOKIE')
        MSG += 'Cookie为空，请设置环境变量YJ_COOKIE\n'
        return
    if not is_logged_in():
        logging.error('未登录或Cookie已失效')
        MSG += '未登录或Cookie已失效\n'
        return
    ('登录成功')

    # 获取签到前的 PB 币
    start_coins = get_pb_coins()
    (f'签到前 PB 币: {start_coins}')

    # 执行任务
    process_tasks()

    # 获取签到后的 PB 币
    end_coins = get_pb_coins()
    (f'签到后 PB 币: {end_coins}')

    # 计算 PB 币差值
    coins_gain =  calculate_pb_coins_difference(start_coins, end_coins)
    MSG += f'签到前 PB 币: {start_coins}\n'
    MSG += f'签到后 PB 币: {end_coins}\n'
    MSG += f'签到后获得的 PB 币: {coins_gain}\n'

def send(key, id, message):
    bot = telepot.Bot(telekey)
    ('正在使用Telebot进行消息推送……')
    bot.sendMessage(id, message, parse_mode=None, disable_web_page_preview=None, disable_notification=None,
                    reply_to_message_id=None, reply_markup=None)
    ('Telebot消息推送完成！')

if __name__ == '__main__':
    logging.basicConfig(
        #level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
    send(telekey, teleid, MSG)
    ('签到完成，消息已发送')