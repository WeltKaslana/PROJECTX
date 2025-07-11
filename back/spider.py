import json
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import openpyxl as op
import os
import pickle
from pyquery import PyQuery as pq
from urllib.parse import quote
from datetime import datetime
from dao import userDAO
import threading
from main import app

# 全局变量
count = 1  # Excel写入计数

# 淘宝登录相关配置
TAOBAO_COOKIE_FILE = "taobao_cookies.pkl"
today = datetime.now().strftime("%Y%m%d")
initiative_id = f"taobao_{today}"

# 京东登录相关配置
JD_COOKIE_FILE = "jd_cookies.pkl"
JD_LOGIN_URL = "https://passport.jd.com/new/login.aspx"  # 京东登录页
JD_HOME_URL = "https://www.jd.com"  # 京东首页
JD_MY_URL = "https://home.jd.com"  # 京东"我的主页"

# -------------------------- 淘宝登录与Cookie处理 --------------------------
def get_taobao_login_cookies():
    """获取淘宝登录Cookie并保存"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    # 反爬机制
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})

    # 打开登录页面
    login_url = "https://login.taobao.com/member/login.jhtml"
    driver.get(login_url)
    print("请在弹出的浏览器中扫码或输入账号密码登录淘宝...")

    # 处理登录过程中可能出现的弹窗
    #handle_taobao_notification_popup(driver)

    # 等待登录成功（检测"我的淘宝"元素）
    WebDriverWait(driver, 180).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.title--OZFmGAMb"))
    )
    print("淘宝登录成功，获取Cookie中...")

    # 获取并保存Cookie
    cookies = driver.get_cookies()
    with open(TAOBAO_COOKIE_FILE, "wb") as f:
        pickle.dump(cookies, f)
    print(f"淘宝Cookie已保存至 {TAOBAO_COOKIE_FILE}")

    return driver

def load_taobao_valid_cookies():
    """加载并验证淘宝Cookie有效性，处理订阅弹窗"""
    if not os.path.exists(TAOBAO_COOKIE_FILE):
        print("未找到淘宝Cookie文件，需要登录获取")
        return get_taobao_login_cookies()

    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    # 反爬机制
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})

    # 先访问淘宝首页建立上下文
    driver.get("https://www.taobao.com")

    # 加载Cookie
    with open(TAOBAO_COOKIE_FILE, "rb") as f:
        cookies = pickle.load(f)

    driver.delete_all_cookies()
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            continue

    # 访问我的淘宝验证登录
    driver.get("https://i.taobao.com/my_itaobao")

    # 处理订阅通知弹窗
    # handle_taobao_notification_popup(driver)

    try:
        # 检测快速登录按钮并点击
        # fast_login_btn = WebDriverWait(driver, 15).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fm-button.fm-submit"))
        # )
        # fast_login_btn.click()

        # # 点击后再次处理可能出现的弹窗
        # handle_taobao_notification_popup(driver)

        # 验证登录成功
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.title--OZFmGAMb"))
        )
        print("淘宝快速登录成功")
    except:
        # 直接验证是否已登录
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.title--OZFmGAMb"))
            )
            print("淘宝Cookie有效，已登录")
        except:
            print("淘宝Cookie失效，重新登录...")
            os.remove(TAOBAO_COOKIE_FILE)
            return get_taobao_login_cookies()

    return driver

# def handle_taobao_notification_popup(driver):
#     """专门处理淘宝"订阅淘宝通知"弹窗，点击"订阅"按钮"""
#     print("检查是否存在淘宝订阅通知弹窗...")
#     try:
#         # 定位弹窗元素
#         popup = WebDriverWait(driver, 8).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.tbpc-global-notification-user-allowed-popup"))
#         )
#         print("检测到淘宝订阅通知弹窗，准备点击'订阅'按钮...")

#         # 定位"订阅"按钮（使用你提供的class和id）
#         agree_btn = popup.find_element(
#             By.CSS_SELECTOR,
#             "button.tbpc-global-notification-user-allowed-popup-deny#nua-deny"
#         )
#         agree_btn.click()
#         print("已点击淘宝'取消'按钮，弹窗关闭")

#         # 等待弹窗完全关闭
#         time.sleep(1)
#     except:
#         print("未检测到淘宝订阅通知弹窗或弹窗已关闭")

# -------------------------- 京东登录与Cookie处理 --------------------------
def get_jd_login_cookies():
    """获取京东登录Cookie并保存"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # 京东反爬较严，建议先关闭无头模式调试
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # 反爬机制
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                          {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})

    # 打开京东登录页
    driver.get(JD_LOGIN_URL)
    print("请在弹出的浏览器中扫码或输入账号密码登录京东...")

    # 等待登录成功（检测"我的京东"元素，核心修改：京东登录成功标识）
    WebDriverWait(driver, 180).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='home.jd.com']"))  # 京东"我的京东"链接
    )
    print("京东登录成功，获取Cookie中...")

    # 获取并保存Cookie
    cookies = driver.get_cookies()
    with open(JD_COOKIE_FILE, "wb") as f:
        pickle.dump(cookies, f)
    print(f"京东Cookie已保存至 {JD_COOKIE_FILE}")

    return driver

def load_jd_valid_cookies():
    """加载并验证京东Cookie有效性"""
    if not os.path.exists(JD_COOKIE_FILE):
        print("未找到京东Cookie文件，需要登录获取")
        return get_jd_login_cookies()

    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # 反爬机制
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                          {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})

    # 先访问京东首页建立上下文
    driver.get(JD_HOME_URL)

    # 加载Cookie
    with open(JD_COOKIE_FILE, "rb") as f:
        cookies = pickle.load(f)

    driver.delete_all_cookies()
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            continue

    # 访问京东"我的主页"验证登录
    driver.get(JD_HOME_URL)

    try:
        # 验证登录成功（京东"我的订单"元素）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='home.jd.com']"))
        )
        print("京东Cookie有效，已登录京东")
        return driver
    except:
        print("京东Cookie已失效，重新登录...")
        os.remove(JD_COOKIE_FILE)
        return get_jd_login_cookies()

# -------------------------- 淘宝爬取逻辑 --------------------------
def taobao_Crawler_main(driver, KEYWORD, pageStart, pageEnd, session_id):
    """淘宝主爬取函数"""
    global wait
    wait = WebDriverWait(driver, 20)
    taobao_goods_list = []
    try:

        # 搜索商品
        taobao_search_goods(driver, KEYWORD)
        # 处理起始页
        if pageStart != 1:
            taobao_turn_pageStart(driver, pageStart)
        taobao_goods_list.extend(taobao_get_goods(driver, pageStart, session_id))
        # 爬取后续页面
        for i in range(pageStart + 1, pageEnd + 1):
            taobao_page_turning(driver, i)
            taobao_goods_list.extend(taobao_get_goods(driver, i, session_id))
    except Exception as exc:
        print(f"淘宝Crawler_main函数错误！Error：{exc}")
    return taobao_goods_list

def taobao_search_goods(driver, KEYWORD):
    """淘宝搜索商品"""
    try:
        print(f"正在淘宝搜索: {KEYWORD}")
        input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#q')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_Search > form > button')))

        input.clear()
        input.send_keys(KEYWORD)
        submit.click()

        time.sleep(2)  # 短暂等待新标签页加载
        handles = driver.window_handles  # 获取所有标签页句柄
        # 如果有新标签页，切换到最新的标签页
        if len(handles) > 1:
            driver.switch_to.window(handles[-1])  # 切换到最新打开的标签页
            print("已切换到淘宝搜索结果标签页")

        time.sleep(2)
        print("淘宝搜索完成！")
    except Exception as exc:
        print(f"淘宝search_goods函数错误！Error：{exc}")

def taobao_page_turning(driver, page_number):
    """淘宝翻页至指定页码"""
    try:
        print(f"正在淘宝翻页至: 第{page_number}页")
        time.sleep(2)
        next_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#search-content-leftWrap button.next-btn.next-medium.next-btn-normal.next-pagination-item.next-next')
        ))
        next_btn.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#search-content-leftWrap span.next-pagination-display > em'),
            str(page_number)
        ))
        print(f"已翻至淘宝第{page_number}页")
    except Exception as exc:
        print(f"淘宝page_turning函数错误！Error：{exc}")

def taobao_turn_pageStart(driver, pageStart):
    """淘宝跳转至起始页"""
    try:
        print(f"正在淘宝跳转至起始页: 第{pageStart}页")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(3)   # 等待页面加载完成

        page_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#search-content-leftWrap span.next-input.next-medium.next-pagination-jump-input > input')
        ))

        page_input.clear()
        page_input.send_keys(pageStart)
        confirm_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#search-content-leftWrap button.next-btn.next-medium.next-btn-normal.next-pagination-jump-go')
        ))

        confirm_btn.click()

        print(f"已跳转至淘宝第{pageStart}页")
    except Exception as exc:
        print(f"淘宝turn_pageStart函数错误！Error：{exc}")

def taobao_scroll_step_by_step(driver, scroll_distance=500, pause_time=1):
    # 重置视图高度为顶部
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)  # 等待页面滚动到顶部

    """淘宝分步滚动页面，解决懒加载问题"""
    print(f"开始淘宝分步滚动页面（每次滚动{scroll_distance}px，停顿{pause_time}秒）...")

    # 初始滚动位置
    last_scroll_top = 0
    # 最大滚动次数（防止无限循环）
    max_attempts = 50
    attempts = 0

    while attempts < max_attempts:
        # 滚动指定距离
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        attempts += 1

        # 停顿等待加载
        time.sleep(pause_time)

        # 获取当前滚动位置
        current_scroll_top = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")

        # 判断是否已滚动到底部
        page_height = driver.execute_script("return document.body.scrollHeight;")
        viewport_height = driver.execute_script("return window.innerHeight;")

        if (current_scroll_top == last_scroll_top) and (current_scroll_top + viewport_height >= page_height - 100):
            print(f"已滚动到淘宝底部（总滚动次数：{attempts}）")
            break

        last_scroll_top = current_scroll_top

    # 最终再滚动到底部确保所有内容加载
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause_time)
    print("淘宝分步滚动完成，所有懒加载内容已加载")

def taobao_get_goods(driver, page, session_id):
    """淘宝获取商品数据"""
    tb_goods_list = []
    try:
        print(f"开始淘宝爬取第{page}页商品数据...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content--CUnfXXxv')))

        time.sleep(2)  # 等待页面加载
        print("开始淘宝滚动页面以加载所有商品...")
        taobao_scroll_step_by_step(driver, scroll_distance=600, pause_time=1.5)

        # 等待商品数据稳定
        previous_count = 0
        consecutive_stable = 0
        while consecutive_stable < 3:
            html = driver.page_source
            doc = pq(html)
            items = []
            for item in doc('div.content--CUnfXXxv > div > div').items():
                if item.find('.title--qJ7Xg_90 span').text() and item.find('.innerPriceWrapper--aAJhHXD4').text():
                    items.append(item)
            current_count = len(items)
            if current_count == previous_count and current_count > 0:
                consecutive_stable += 1
            else:
                consecutive_stable = 0
                previous_count = current_count
            time.sleep(0.5)

        print(f"淘宝第{page}页共识别出{current_count}个有效商品")

        # 提取并保存商品数据
        success_count = 0
        fail_count = 0
        for item in items:
            try:
                # 提取商品信息
                name = item.find('.title--qJ7Xg_90 span').text().strip()

                # 价格处理
                price_text = item.find('.innerPriceWrapper--aAJhHXD4').text().replace('\n', '').replace('\r', '')
                price = float(price_text) if price_text else 0.0

                # 销量处理
                deal_text = item.find('.realSales--XZJiepmt').text()
                deal_text = deal_text.replace("万", "0000").split("人")[0].split("+")[0].strip()
                deals = int(deal_text) if deal_text else 0

                # 处理链接
                goods_url = item.find('.doubleCardWrapperAdapt--mEcC7olq').attr('href') or ''
                shop_url = item.find('.TextAndPic--grkZAtsC a').attr('href') or ''
                img_url = item.find('.mainPicAdaptWrapper--V_ayd2hD img').attr('src') or ''
                
                if img_url == '':
                    fail_count += 1
                    continue 
                goods = {

                    "商品名称": name,
                    "价格": price,
                    "图片": img_url,
                    "店铺链接": shop_url,
                    "商品链接": goods_url,
                    "交易量": deals,
                    
                }

                
                tb_goods_list.append(goods)

                # 保存商品到数据库
                userDAO.add_goods(
                    session_id=session_id,
                    name=name,
                    price=price,
                    img_url=img_url,
                    shop_url=shop_url,
                    goods_url=goods_url,
                    deals=deals,
                    
                )
                success_count += 1
            except Exception as e:
                fail_count += 1
                print(e)
                continue

        print(f"淘宝第{page}页爬取完成：成功{success_count}个，失败{fail_count}个")

    except Exception as exc:
        print(f"淘宝get_goods函数错误！Error：{exc}")
    return tb_goods_list

# -------------------------- 京东爬取逻辑 --------------------------
def jd_Crawler_main(driver, KEYWORD, pageStart, pageEnd, session_id):
    """京东主爬取函数"""
    global wait
    wait = WebDriverWait(driver, 20)
    jingdong_goods_list = []
    try:
        # 搜索商品
        jd_search_goods(driver, KEYWORD)
        # 处理起始页
        if pageStart != 1:
            jd_turn_pageStart(driver, pageStart)
        jingdong_goods_list.extend(jd_get_goods(driver, pageStart, session_id))
        # 爬取后续页面
        for i in range(pageStart + 1, pageEnd + 1):
            jd_page_turning(driver, i)
            jingdong_goods_list.extend(jd_get_goods(driver, i, session_id))     
    except Exception as exc:
        print(f"京东Crawler_main函数错误！Error：{exc}")
    return jingdong_goods_list


def jd_search_goods(driver, KEYWORD):
    """京东搜索商品"""
    try:
        print(f"正在京东搜索商品: {KEYWORD}")
        # 京东搜索框（核心修改：选择器替换）
        input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#key')))  # 京东搜索框ID为"key"
        # 京东搜索按钮（核心修改：选择器替换）
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search button')))

        input.clear()
        input.send_keys(KEYWORD)
        submit.click()
        time.sleep(2)

        # 京东搜索可能打开新标签页，切换到最新标签页
        handles = driver.window_handles
        if len(handles) > 1:
            driver.switch_to.window(handles[-1])
        print("京东搜索完成！")
    except Exception as exc:
        print(f"京东search_goods函数错误！Error：{exc}")

def jd_page_turning(driver, page_number):
    """京东翻页至指定页码"""
    try:
        print(f"正在京东翻页至第{page_number}页")
        time.sleep(2)
        # 京东下一页按钮（核心修改：选择器替换）
        next_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a.pn-next')  # 京东下一页按钮
        ))
        next_btn.click()
        # 验证页码（京东当前页码标识）
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'span.p-num a.curr'),  # 京东当前页码
            str(page_number)
        ))
        print(f"已翻至京东第{page_number}页")
    except Exception as exc:
        print(f"京东page_turning函数错误！Error：{exc}")

def jd_turn_pageStart(driver, pageStart):
    """京东跳转至起始页"""
    try:
        print(f"正在京东跳转至第{pageStart}页")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 京东页码输入框（核心修改：选择器替换）
        page_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input#jumpPage'))  # 京东页码输入框
        )
        page_input.clear()
        page_input.send_keys(pageStart)

        # 京东跳转确认按钮（核心修改：选择器替换）
        confirm_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a.btn.btn-default'))  # 京东确认按钮
        )
        confirm_btn.click()
        print(f"已跳转至京东第{pageStart}页")
    except Exception as exc:
        print(f"京东turn_pageStart函数错误！Error：{exc}")

# 京东懒加载解决（京东商品列表懒加载较明显）
def jd_scroll_step_by_step(driver, scroll_distance=600, pause_time=1):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)
    print(f"开始京东滚动页面加载商品...")

    last_scroll_top = 0
    max_attempts = 50
    attempts = 0

    while attempts < max_attempts:
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        attempts += 1
        time.sleep(pause_time)

        current_scroll_top = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
        page_height = driver.execute_script("return document.body.scrollHeight;")
        viewport_height = driver.execute_script("return window.innerHeight;")

        if (current_scroll_top == last_scroll_top) and (current_scroll_top + viewport_height >= page_height - 100):
            print(f"已滚动到京东页面底部（总次数：{attempts}）")
            break
        last_scroll_top = current_scroll_top

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause_time)
    print("京东商品懒加载内容已加载")

def jd_get_goods(driver, page, session_id):
    """获取京东商品数据（核心：京东商品元素选择器）"""
    jd_goods_list = []
    try:
        global count
        print(f"开始京东爬取第{page}页商品数据...")
        # 等待京东商品列表加载（核心修改：容器选择器）
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList')))  # 京东商品列表容器
        time.sleep(1)

        # 滚动加载所有商品
        jd_scroll_step_by_step(driver)

        
        # 等待商品数据稳定
        previous_count = 0
        consecutive_stable = 0
        while consecutive_stable < 3:
            html = driver.page_source
            doc = pq(html)
            items = []
            for item in doc('li.gl-item').items():
                # if item.attr('data-spu').strip() != '':
                    # 只处理有SPU数据的商品
                    items.append(item)
            current_count = len(items)
            
            if current_count == previous_count and current_count > 0:
                consecutive_stable += 1
            else:
                consecutive_stable = 0
                previous_count = current_count
            time.sleep(0.5)

        print(f"第{page}页共识别出{current_count}个有效商品")
        
        # 提取并保存商品数据
        success_count = 0
        fail_count = 0

        for item in items:
            try:
                # 京东商品标题（核心修改：选择器）
                title = item.find('.p-name em').text().strip().replace('\n', '')

                # 京东商品价格（核心修改：选择器）
                price_text = item.find('.p-price i').text().strip()
                price = float(price_text) if price_text else 0.0

                # 京东商品销量（核心修改：选择器）
                deal_text = item.find('.p-commit a').text().strip()
                deal_text = deal_text.replace("万+", "0000").replace("+", "").split("条")[0].strip()
                deals = int(float(deal_text)) if deal_text else 0


                # 商品链接（核心修改：选择器）
                goods_url = item.find('.p-name a').attr('href') or ''
                if goods_url.startswith('//'):
                    goods_url = f'https:{goods_url}'
                elif not goods_url.startswith('http'):
                    goods_url = f'https://item.jd.com{goods_url}'

                # 店铺链接（核心修改：选择器）
                shop_url = item.find('.p-shop a').attr('href') or ''
                if shop_url.startswith('//'):
                    shop_url = f'https:{shop_url}'

                # 商品图片（核心修改：选择器）
                img_url = item.find('.p-img img').attr('src') or item.find('.p-img img').attr('data-lazy-img') or ''
                if img_url.startswith('//'):
                    img_url = f'https:{img_url}'

                goods = {
                    "商品名称": title,
                    "价格": price,
                    "图片": img_url,
                    "店铺链接": shop_url,
                    "商品链接": goods_url,
                    "交易量": deals,
                   
                }
                jd_goods_list.append(goods)
                # 保存商品到数据库
                userDAO.add_goods(
                    session_id=session_id,
                    name=title,
                    price=price,
                    img_url=img_url,
                    shop_url=shop_url,
                    goods_url=goods_url,
                    deals=deals,
                    
                )

                success_count += 1
            except Exception as e:
                fail_count += 1
                print(e)
                continue

        print(f"京东第{page}页爬取完成：成功{success_count}个，失败{fail_count}个")

    except Exception as exc:
        print(f"京东get_goods函数错误！Error：{exc}")
    return jd_goods_list

# 保存json文件
def save_json_result(data, session_id):
    """保存爬取结果到JSON文件"""
    try:
        # 创建保存目录（如果不存在）
        output_dir = "json_results"
        os.makedirs(output_dir, exist_ok=True)

        # 生成文件名（使用session_id和时间戳确保唯一性）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{output_dir}/result_{session_id}_{timestamp}.json"

        # 写入JSON文件（使用UTF-8编码防止中文乱码）
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"JSON文件已保存: {file_name}")
        return file_name

    except Exception as e:
        print(f"保存JSON文件失败: {e}")
        return None

def crawler(keys, session_id):
    goods_list = []
    lock = threading.Lock()
    if keys:  # 当flag为True且keys列表不为空时执行爬取
        pageStart = 1
        pageEnd = 1
        # 将关键词列表转换为字符串（用空格连接）
        combined_keyword = ' '.join(keys)
        print(f"开始爬取组合关键词: {combined_keyword}")

        # 获取淘宝登录后的浏览器实例
        taobao_driver = load_taobao_valid_cookies()
        # 获取京东登录后的浏览器实例
        jd_driver = load_jd_valid_cookies()

        # 定义线程函数
        def taobao_crawl():
            nonlocal goods_list
            with app.app_context(): 
                taobao_goods = taobao_Crawler_main(taobao_driver, combined_keyword, pageStart, pageEnd, session_id)
            with lock:
                goods_list.extend(taobao_goods)

        def jingdong_crawl():
            nonlocal goods_list
            with app.app_context():
                jingdong_goods = jd_Crawler_main(jd_driver, combined_keyword, pageStart, pageEnd, session_id)       
            with lock:
                goods_list.extend(jingdong_goods)

        # 创建线程
        taobao_thread = threading.Thread(target=taobao_crawl)
        jd_thread = threading.Thread(target=jingdong_crawl)

        # 启动线程
        taobao_thread.start()
        jd_thread.start()

        # 等待线程完成
        taobao_thread.join()
        jd_thread.join()

        # 关闭浏览器
        taobao_driver.quit()
        jd_driver.quit()

    # 构建返回结果
    result_data = {
        "keywords": keys,
        "session_id": session_id,
        "goods": goods_list
    }

    # 保存JSON文件
    save_json_result(result_data, session_id)

    # 返回JSON字符串
    # return json.dumps(result_data, ensure_ascii=False, indent=2)

def test():
    # 仅在直接运行此文件时执行以下代码
    test_keys = ["手机", "5G"]
    crawler(test_keys, session_id='xDJTomato_0001')
    # print(result_json)

