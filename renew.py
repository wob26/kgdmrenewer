#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_chrome_version():
    """获取 GitHub Actions 环境中 Chrome 的主版本号"""
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        version = output.strip().split()[-1].split('.')[0]
        print(f"🔎 检测到环境 Chrome 版本: {version}")
        return int(version)
    except Exception:
        return None

def setup_driver():
    """创建浏览器，强制同步版本号"""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    version = get_chrome_version()
    try:
        # 强制要求 uc 使用和系统一致的主版本号，防止 144 和 145 这种错位
        driver = uc.Chrome(options=options, version_main=version)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"❌ 浏览器启动失败: {e}")
        # 如果还是失败，尝试不带版本号的保底方案
        return uc.Chrome(options=options)

def wait_and_click(driver, xpath, timeout=20):
    """更强力的点击逻辑"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        return False

def login_account(driver, username, password):
    """针对新的 DigitalPlat 登录页适配"""
    try:
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        print("⏳ 等待登录页面加载...")
        time.sleep(10) # 留足时间过 Cloudflare
        
        # 寻找 Email 输入框
        email_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.send_keys(username)
        
        # 点击 Next (可能是 button 也可能是包含文字的元素)
        wait_and_click(driver, "//button[contains(., 'Next')]")
        time.sleep(3)
        
        # 寻找密码框
        pwd_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        pwd_field.send_keys(password)
        
        # 点击 Login
        wait_and_click(driver, "//button[contains(., 'Login')]")
        time.sleep(10)
        
        return "auth/login" not in driver.current_url
    except Exception as e:
        print(f"❌ 登录出错: {e}")
        return False

def renew_domain(driver, domain):
    """点击流程: Renew -> Request free renewal"""
    try:
        # 直接跳到该域名的管理页
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"🌐 访问管理页: {domain}")
        driver.get(url)
        time.sleep(8)
        
        # 1. 点击 Renew 按钮（可能是面板上的一个页签或按钮）
        print(f"🔘 尝试寻找并点击 Renew 按钮...")
        # 尝试多种可能的 XPath
        renew_xpaths = [
            "//button[contains(., 'Renew')]",
            "//a[contains(., 'Renew')]",
            "//span[contains(text(), 'Renew')]/.."
        ]
        
        found_renew = False
        for xpath in renew_xpaths:
            if wait_and_click(driver, xpath, timeout=10):
                found_renew = True
                break
        
        if not found_renew:
            print("⚠️ 未找到 Renew 按钮，可能页面结构已变或权限问题")
            return False
            
        time.sleep(5)
        
        # 2. 点击 Request free renewal 按钮
        print(f"🚀 尝试点击 Request free renewal...")
        request_xpath = "//button[contains(., 'Request free renewal')]"
        if wait_and_click(driver, request_xpath, timeout=15):
            print(f"✅ {domain} 续期请求已发送")
            time.sleep(5)
            return True
        else:
            if "180 days" in driver.page_source:
                print(f"ℹ️ {domain} 还没到续期时间(需少于180天)")
            else:
                print(f"❌ 未找到确认续期的按钮")
            return False
            
    except Exception as e:
        print(f"❌ {domain} 处理异常: {e}")
        return False

def main():
    idx = 1
    while True:
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if not user or not pwd:
            break
            
        print(f"\n{'='*40}\n账户 {idx}: {user}\n{'='*40}")
        driver = None
        try:
            driver = setup_driver()
            if login_account(driver, user, pwd):
                print("🔓 登录成功，开始检查域名")
                domain_list = [d.strip() for d in doms.split(',') if d.strip()]
                for d in domain_list:
                    renew_domain(driver, d)
            else:
                print("❌ 登录失败，请检查账号密码或 Secret 配置")
        finally:
            if driver:
                driver.quit()
        idx += 1
        time.sleep(5)

if __name__ == "__main__":
    main()