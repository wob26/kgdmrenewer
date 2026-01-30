#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigitalPlat 域名自动续期脚本 - 修复版
"""

import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_options():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return options

def setup_driver():
    """创建浏览器，自动适配版本"""
    try:
        # 不再指定 version_main，让它自动检测
        driver = uc.Chrome(options=get_options())
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}")
        raise

def wait_and_click(driver, xpath, timeout=15):
    """封装的点击函数，更稳健"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        # 使用 JS 点击，防止被元素遮挡
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        return False

def login_account(driver, username, password):
    """登录逻辑"""
    try:
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        time.sleep(10) # 等待 Cloudflare 盾
        
        # 输入邮箱
        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(username)
        
        # 点击 Next
        wait_and_click(driver, "//button[contains(., 'Next')]")
        time.sleep(3)
        
        # 输入密码
        pwd_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        pwd_input.send_keys(password)
        
        # 点击 Login
        wait_and_click(driver, "//button[contains(., 'Login')]")
        time.sleep(10)
        
        if "login" not in driver.current_url.lower():
            print("✅ 登录成功")
            return True
        return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def renew_domain(driver, domain):
    """续期逻辑：点击 Renew 标签 -> 点击 Request free renewal"""
    try:
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"  > 正在处理: {domain}")
        driver.get(url)
        time.sleep(5)
        
        # 1. 点击 Renew 按钮/标签
        # 兼容按钮和链接形式
        renew_xpath = "//button[contains(text(), 'Renew')] | //a[contains(text(), 'Renew')] | //span[contains(text(), 'Renew')]"
        if not wait_and_click(driver, renew_xpath):
            print(f"  ⚠️ 未找到 Renew 按钮，可能已失效或结构改变")
            return False
        
        time.sleep(3)
        
        # 2. 点击 Request free renewal 按钮
        request_xpath = "//button[contains(text(), 'Request free renewal')]"
        if wait_and_click(driver, request_xpath):
            print(f"  🚀 已点击 Request free renewal 按钮")
            time.sleep(5)
            # 简单判断是否成功
            if "success" in driver.page_source.lower() or "180" in driver.page_source:
                print(f"  ✅ {domain} 续期操作完成")
                return True
        else:
            if "180 days" in driver.page_source:
                print(f"  ℹ️ {domain} 尚在有效期内，无需续期")
            else:
                print(f"  ❌ 未找到最后的续期确认按钮")
        return False
    except Exception as e:
        print(f"  ❌ 续期执行异常: {e}")
        return False

def main():
    idx = 1
    while True:
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if not user or not pwd:
            break
            
        print(f"\n==== 正在处理账户 {idx}: {user} ====")
        driver = None
        try:
            driver = setup_driver()
            if login_account(driver, user, pwd):
                domain_list = [d.strip() for d in doms.split(',') if d.strip()]
                for d in domain_list:
                    renew_domain(driver, d)
        except Exception as e:
            print(f"❌ 账户 {idx} 运行错误: {e}")
        finally:
            if driver:
                driver.quit()
        idx += 1
        time.sleep(5)

if __name__ == "__main__":
    main()