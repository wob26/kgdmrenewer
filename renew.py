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
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        return int(output.strip().split()[-1].split('.')[0])
    except:
        return None

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # 增加反爬指纹伪装
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    version = get_chrome_version()
    driver = uc.Chrome(options=options, version_main=version)
    driver.set_page_load_timeout(60)
    return driver

def save_debug_screenshot(driver, name):
    filename = f"debug_{name}.png"
    driver.save_screenshot(filename)
    print(f"📸 截图已保存: {filename}")

def wait_and_click(driver, selector, by=By.XPATH, timeout=20):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        return False

def login_account(driver, username, password, acc_idx):
    try:
        print("🌐 正在访问登录页...")
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        
        # --- 步骤 1: 邮箱 ---
        print("📧 正在输入邮箱...")
        # 使用你截图中的 id="email"
        email_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.clear()
        email_field.send_keys(username)
        
        # 点击 Next 按钮
        wait_and_click(driver, "//button[contains(text(), 'Next')]")
        time.sleep(3)
        
        # --- 步骤 2: 密码 ---
        print("🔑 正在输入密码...")
        # 等待密码框 id="password" 出现
        pwd_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        pwd_field.clear()
        pwd_field.send_keys(password)
        
        # --- 步骤 3: 处理验证码 ---
        # 截图显示有 Cloudflare Turnstile 验证码
        print("🛡️ 检测验证码状态...")
        time.sleep(5) # 给验证码一点加载时间
        
        # 尝试点击 Login 按钮
        # 截图显示该按钮没有 ID，但有 class="btn-primary" 和文字 "Login"
        login_btn_xpath = "//button[contains(text(), 'Login')]"
        
        print("🚀 尝试登录...")
        if not wait_and_click(driver, login_btn_xpath):
            save_debug_screenshot(driver, f"acc{acc_idx}_no_login_btn")
            return False

        # 等待跳转
        time.sleep(10)
        
        if "login" not in driver.current_url.lower():
            return True
        else:
            print("❌ 登录未成功，可能卡在验证码环节")
            save_debug_screenshot(driver, f"acc{acc_idx}_stuck_login")
            return False
            
    except Exception as e:
        print(f"❌ 登录过程发生错误: {e}")
        save_debug_screenshot(driver, f"acc{acc_idx}_error")
        return False

def renew_domain(driver, domain):
    try:
        # 按照你描述的链接格式直接访问
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"🔎 正在处理域名: {domain}")
        driver.get(url)
        time.sleep(8)
        
        # 第一步：点击 Renew 按钮
        print("  - 寻找 Renew 按钮...")
        # 适配新版 UI 结构
        renew_xpath = "//button[contains(., 'Renew')] | //a[contains(., 'Renew')]"
        if not wait_and_click(driver, renew_xpath):
            print(f"  ⚠️ 未找到 Renew 按钮，可能已失效")
            return False
            
        time.sleep(4)
        
        # 第二步：点击 Request free renewal
        print("  - 点击 Request free renewal...")
        request_xpath = "//button[contains(., 'Request free renewal')]"
        if wait_and_click(driver, request_xpath):
            print(f"  ✅ {domain} 续期请求成功")
            return True
        else:
            print(f"  ℹ️ {domain} 暂不可续期")
            return False
            
    except Exception as e:
        print(f"❌ {domain} 续期失败: {e}")
        return False

def main():
    idx = 1
    while True:
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if not user or not pwd: break
            
        print(f"\n{'='*50}\n账户 {idx}: {user}\n{'='*50}")
        driver = None
        try:
            driver = setup_driver()
            if login_account(driver, user, pwd, idx):
                print("🔓 登录成功！")
                for d in [d.strip() for d in doms.split(',') if d.strip()]:
                    renew_domain(driver, d)
            else:
                print("⏭️ 跳过当前账户")
        finally:
            if driver: driver.quit()
        idx += 1
        time.sleep(5)

if __name__ == "__main__":
    main()