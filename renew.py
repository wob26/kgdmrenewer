#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigitalPlat 域名自动续期脚本
使用 undetected-chromedriver 绕过 Cloudflare 验证
"""

import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """配置并创建 undetected Chrome WebDriver"""
    options = uc.ChromeOptions()
    
    # 无头模式
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        # 使用 undetected_chromedriver（自动绕过检测）
        driver = uc.Chrome(options=options, version_main=131)  # 使用Chrome 131
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"❌ 创建浏览器失败: {e}")
        # 如果指定版本失败，尝试自动检测
        try:
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(60)
            return driver
        except Exception as e2:
            print(f"❌ 再次失败: {e2}")
            raise

def wait_element(driver, by, value, timeout=20, clickable=False):
    """等待元素"""
    try:
        if clickable:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        else:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
    except TimeoutException:
        return None

def login_account(driver, account_num, username, password):
    """登录账户"""
    try:
        print(f"[账户 {account_num}] 打开登录页...")
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        time.sleep(8)  # 等待Cloudflare验证自动完成
        
        # 步骤1: 输入邮箱
        print(f"[账户 {account_num}] 输入邮箱...")
        email_field = None
        
        # 多种定位方式
        selectors = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@placeholder='you@example.com']"),
            (By.XPATH, "//input[contains(@placeholder, '@')]"),
        ]
        
        for by, val in selectors:
            email_field = wait_element(driver, by, val, timeout=5)
            if email_field:
                print(f"[账户 {account_num}] ✓ 找到邮箱框")
                break
        
        if not email_field:
            print(f"❌ [账户 {account_num}] 未找到邮箱框")
            driver.save_screenshot(f"error_email_{account_num}.png")
            return False
        
        email_field.clear()
        email_field.send_keys(username)
        time.sleep(2)
        
        # 步骤2: 点击Next
        print(f"[账户 {account_num}] 点击Next...")
        next_btn = wait_element(driver, By.XPATH, "//button[@type='submit' or contains(text(), 'Next')]", timeout=10, clickable=True)
        if not next_btn:
            print(f"❌ [账户 {account_num}] 未找到Next按钮")
            return False
        
        next_btn.click()
        time.sleep(6)
        
        # 步骤3: 输入密码
        print(f"[账户 {account_num}] 输入密码...")
        pwd_field = wait_element(driver, By.CSS_SELECTOR, "input[type='password']", timeout=10)
        if not pwd_field:
            print(f"❌ [账户 {account_num}] 未找到密码框")
            return False
        
        pwd_field.clear()
        pwd_field.send_keys(password)
        time.sleep(2)
        
        # 步骤4: 点击Login
        print(f"[账户 {account_num}] 点击Login...")
        login_btn = wait_element(driver, By.XPATH, "//button[@type='submit' or contains(text(), 'Login')]", timeout=10, clickable=True)
        if not login_btn:
            print(f"❌ [账户 {account_num}] 未找到Login按钮")
            return False
        
        login_btn.click()
        time.sleep(8)
        
        # 验证登录
        if "login" not in driver.current_url.lower():
            print(f"✅ [账户 {account_num}] 登录成功!")
            return True
        else:
            print(f"❌ [账户 {account_num}] 登录失败")
            driver.save_screenshot(f"error_login_{account_num}.png")
            return False
        
    except Exception as e:
        print(f"❌ [账户 {account_num}] 登录异常: {e}")
        return False

def renew_domain(driver, account_num, domain):
    """续期域名"""
    try:
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"  [{domain}] 访问管理页...")
        driver.get(url)
        time.sleep(5)
        
        # 点击Renew标签
        print(f"  [{domain}] 点击Renew...")
        renew_tab = wait_element(driver, By.XPATH, "//button[contains(text(), 'Renew')] | //a[contains(text(), 'Renew')]", timeout=10, clickable=True)
        if not renew_tab:
            print(f"  ⚠️ [{domain}] 未找到Renew标签")
            return False
        
        driver.execute_script("arguments[0].click();", renew_tab)
        time.sleep(4)
        
        # 点击Request free renewal
        print(f"  [{domain}] 点击续期按钮...")
        renew_btn = wait_element(driver, By.XPATH, "//button[contains(text(), 'Request free renewal')]", timeout=10, clickable=True)
        if not renew_btn:
            if "180 days" in driver.page_source:
                print(f"  ℹ️ [{domain}] 不在续期窗口(需<180天)")
            else:
                print(f"  ⚠️ [{domain}] 未找到续期按钮")
            return False
        
        driver.execute_script("arguments[0].click();", renew_btn)
        time.sleep(5)
        
        # 检查结果
        page = driver.page_source.lower()
        if any(kw in page for kw in ["success", "renewed", "updated"]):
            print(f"  ✅ [{domain}] 续期成功!")
            return True
        else:
            print(f"  ⚠️ [{domain}] 状态未知")
            return False
        
    except Exception as e:
        print(f"  ❌ [{domain}] 续期异常: {e}")
        return False

def process_account(num, username, password, domains):
    """处理账户"""
    print(f"\n{'='*60}")
    print(f"[账户 {num}: {username}]")
    print(f"{'='*60}")
    
    if not domains:
        print(f"[账户 {num}] 无域名配置")
        return
    
    driver = None
    try:
        print(f"[账户 {num}] 启动浏览器...")
        driver = setup_driver()
        
        if not login_account(driver, num, username, password):
            return
        
        domain_list = [d.strip() for d in domains.split(',') if d.strip()]
        print(f"[账户 {num}] 共{len(domain_list)}个域名")
        
        success = 0
        for i, domain in enumerate(domain_list, 1):
            print(f"\n[{i}/{len(domain_list)}] {domain}")
            if renew_domain(driver, num, domain):
                success += 1
            time.sleep(2)
        
        print(f"\n[账户 {num}] 完成: {success}/{len(domain_list)}")
        
    except Exception as e:
        print(f"❌ [账户 {num}] 异常: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print(f"[账户 {num}] 浏览器已关闭")
            except:
                pass

def main():
    print("="*60)
    print("DigitalPlat 域名续期脚本")
    print("版本: 2025-01-30 (undetected-chromedriver)")
    print("="*60)
    
    idx = 1
    count = 0
    
    while True:
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if user and pwd:
            process_account(idx, user, pwd, doms)
            count += 1
            idx += 1
            
            if os.environ.get(f'ACCOUNT_{idx}_USERNAME'):
                print(f"\n等待5秒...")
                time.sleep(5)
        else:
            if idx == 1:
                print("\n❌ 未找到账户配置")
                print("需要设置: ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD, ACCOUNT_1_DOMAINS")
            break
    
    print(f"\n{'='*60}")
    print(f"处理完成: {count}个账户")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
