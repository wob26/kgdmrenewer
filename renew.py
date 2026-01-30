#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigitalPlat 域名自动续期脚本
适配新版 DigitalPlat Domain Dashboard (2025年1月版本)
支持两步登录流程和Cloudflare验证
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """
    配置并创建 Chrome WebDriver
    """
    os.environ['WDM_SSL_VERIFY'] = '0'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    # 添加user-agent，看起来更像真实浏览器
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"❌ 创建浏览器驱动失败: {e}")
        raise

def wait_and_find_element(driver, by, value, timeout=20, clickable=False):
    """等待并查找页面元素"""
    try:
        if clickable:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        else:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        return element
    except TimeoutException:
        return None

def wait_for_cloudflare(driver, max_wait=30):
    """
    等待Cloudflare验证完成
    检测页面中是否有Cloudflare验证，如果有则等待
    """
    print("  检查Cloudflare验证...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # 检查是否有Cloudflare验证框
            cf_challenge = driver.find_elements(By.XPATH, "//*[contains(text(), '确认您是真人') or contains(text(), 'Verify you are human') or contains(@class, 'cf-') or contains(@id, 'cf-')]")
            
            if not cf_challenge:
                print("  ✓ 无需Cloudflare验证或已通过")
                return True
            
            print(f"  等待Cloudflare验证... ({int(time.time() - start_time)}s)")
            time.sleep(2)
        except:
            return True
    
    print(f"  ⚠️ Cloudflare验证等待超时({max_wait}s)")
    return False

def login_account(driver, account_num, username, password):
    """
    登录到 DigitalPlat 账户
    两步登录: 邮箱 -> Next -> 密码 -> Login
    """
    try:
        login_url = "https://dash.domain.digitalplat.org/auth/login"
        print(f"[账户 {account_num}] 正在打开登录页面: {login_url}")
        driver.get(login_url)
        time.sleep(5)
        
        # 等待Cloudflare验证（如果有）
        wait_for_cloudflare(driver, max_wait=30)
        
        # ========== 第一步: 输入邮箱 ==========
        print(f"[账户 {account_num}] 步骤1: 查找邮箱输入框...")
        email_field = None
        
        # 尝试更多定位方式
        email_selectors = [
            # 按placeholder查找
            (By.XPATH, "//input[contains(@placeholder, 'example.com')]"),
            (By.XPATH, "//input[contains(@placeholder, '@')]"),
            (By.XPATH, "//input[@placeholder='you@example.com']"),
            # 按label查找
            (By.XPATH, "//label[contains(text(), 'E-MAIL')]/..//input"),
            (By.XPATH, "//label[contains(text(), 'Email')]/..//input"),
            (By.XPATH, "//*[contains(text(), 'E-MAIL')]/following::input[1]"),
            # 按type查找
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@type='email']"),
            # 按name/id查找
            (By.NAME, "email"),
            (By.ID, "email"),
            (By.NAME, "identifier"),
            # 通用查找：页面上第一个input
            (By.CSS_SELECTOR, "input:not([type='hidden']):not([type='submit'])"),
        ]
        
        for by, value in email_selectors:
            try:
                email_field = wait_and_find_element(driver, by, value, timeout=3)
                if email_field and email_field.is_displayed():
                    print(f"[账户 {account_num}] ✓ 找到邮箱输入框")
                    break
            except:
                continue
        
        if not email_field:
            print(f"❌ [账户 {account_num}] 未找到邮箱输入框")
            print(f"   当前URL: {driver.current_url}")
            # 打印页面上所有input元素，帮助调试
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"   页面上共有 {len(inputs)} 个input元素:")
                for i, inp in enumerate(inputs[:5]):  # 只显示前5个
                    print(f"     {i+1}. type={inp.get_attribute('type')}, "
                          f"name={inp.get_attribute('name')}, "
                          f"placeholder={inp.get_attribute('placeholder')}")
            except:
                pass
            
            driver.save_screenshot(f"login_step1_failed_account_{account_num}.png")
            return False
        
        # 清空并输入邮箱
        try:
            email_field.clear()
        except:
            pass
        email_field.send_keys(username)
        time.sleep(2)
        
        # ========== 第二步: 点击 Next 按钮 ==========
        print(f"[账户 {account_num}] 步骤2: 查找 Next 按钮...")
        next_button = None
        
        next_selectors = [
            (By.XPATH, "//button[normalize-space()='Next']"),
            (By.XPATH, "//button[contains(text(), 'Next')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[contains(@class, 'submit')]"),
        ]
        
        for by, value in next_selectors:
            try:
                next_button = wait_and_find_element(driver, by, value, timeout=3, clickable=True)
                if next_button and next_button.is_displayed():
                    print(f"[账户 {account_num}] ✓ 找到 Next 按钮")
                    break
            except:
                continue
        
        if not next_button:
            print(f"❌ [账户 {account_num}] 未找到 Next 按钮")
            driver.save_screenshot(f"login_step2_failed_account_{account_num}.png")
            return False
        
        next_button.click()
        time.sleep(5)
        
        # 再次等待Cloudflare（密码页面可能也有）
        wait_for_cloudflare(driver, max_wait=30)
        
        # ========== 第三步: 输入密码 ==========
        print(f"[账户 {account_num}] 步骤3: 查找密码输入框...")
        password_field = None
        
        password_selectors = [
            (By.XPATH, "//input[@type='password']"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.XPATH, "//label[contains(text(), 'PASSWORD')]/..//input"),
            (By.XPATH, "//label[contains(text(), 'Password')]/..//input"),
        ]
        
        for by, value in password_selectors:
            try:
                password_field = wait_and_find_element(driver, by, value, timeout=3)
                if password_field and password_field.is_displayed():
                    print(f"[账户 {account_num}] ✓ 找到密码输入框")
                    break
            except:
                continue
        
        if not password_field:
            print(f"❌ [账户 {account_num}] 未找到密码输入框")
            driver.save_screenshot(f"login_step3_failed_account_{account_num}.png")
            return False
        
        try:
            password_field.clear()
        except:
            pass
        password_field.send_keys(password)
        time.sleep(2)
        
        # ========== 第四步: 点击 Login 按钮 ==========
        print(f"[账户 {account_num}] 步骤4: 查找 Login 按钮...")
        login_button = None
        
        login_selectors = [
            (By.XPATH, "//button[normalize-space()='Login']"),
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//input[@type='submit']"),
        ]
        
        for by, value in login_selectors:
            try:
                login_button = wait_and_find_element(driver, by, value, timeout=3, clickable=True)
                if login_button and login_button.is_displayed():
                    print(f"[账户 {account_num}] ✓ 找到 Login 按钮")
                    break
            except:
                continue
        
        if not login_button:
            print(f"❌ [账户 {account_num}] 未找到 Login 按钮")
            driver.save_screenshot(f"login_step4_failed_account_{account_num}.png")
            return False
        
        login_button.click()
        time.sleep(8)
        
        # ========== 验证登录 ==========
        print(f"[账户 {account_num}] 步骤5: 验证登录状态...")
        current_url = driver.current_url
        
        if "login" not in current_url.lower():
            print(f"✅ [账户 {account_num}] 登录成功! 当前页面: {current_url}")
            return True
        
        # 检查错误信息
        try:
            page_text = driver.page_source.lower()
            if any(err in page_text for err in ['invalid', 'incorrect', 'wrong', 'error', 'failed']):
                print(f"❌ [账户 {account_num}] 登录失败: 用户名或密码错误")
            else:
                print(f"❌ [账户 {account_num}] 登录失败: 原因未知")
        except:
            print(f"❌ [账户 {account_num}] 登录失败")
        
        driver.save_screenshot(f"login_failed_final_account_{account_num}.png")
        return False
        
    except Exception as e:
        print(f"❌ [账户 {account_num}] 登录过程异常: {e}")
        try:
            driver.save_screenshot(f"login_exception_account_{account_num}.png")
        except:
            pass
        return False

def renew_single_domain(driver, account_num, domain):
    """续期单个域名"""
    try:
        domain_manage_url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"  [域名: {domain}] 正在访问管理页面...")
        driver.get(domain_manage_url)
        time.sleep(4)
        
        # 等待Cloudflare
        wait_for_cloudflare(driver)
        
        # 点击 Renew 标签
        print(f"  [域名: {domain}] 查找 Renew 标签...")
        renew_button = None
        selectors = [
            "//button[normalize-space()='Renew']",
            "//button[contains(text(), 'Renew')]",
            "//a[contains(text(), 'Renew')]",
            "//*[contains(@class, 'tab') and contains(text(), 'Renew')]",
            "//*[@role='tab' and contains(text(), 'Renew')]",
        ]
        
        for selector in selectors:
            renew_button = wait_and_find_element(driver, By.XPATH, selector, timeout=5, clickable=True)
            if renew_button:
                break
        
        if not renew_button:
            print(f"  ⚠️ [域名: {domain}] 未找到 Renew 标签")
            driver.save_screenshot(f"renew_tab_not_found_{domain}.png")
            return False
        
        print(f"  [域名: {domain}] 点击 Renew 标签...")
        driver.execute_script("arguments[0].scrollIntoView(true);", renew_button)
        time.sleep(1)
        renew_button.click()
        time.sleep(4)
        
        # 点击 Request free renewal 按钮
        print(f"  [域名: {domain}] 查找续期按钮...")
        renewal_button = None
        selectors = [
            "//button[contains(text(), 'Request free renewal')]",
            "//button[contains(text(), 'Free renewal')]",
            "//button[contains(., 'Request') and contains(., 'free')]",
        ]
        
        for selector in selectors:
            renewal_button = wait_and_find_element(driver, By.XPATH, selector, timeout=5, clickable=True)
            if renewal_button:
                break
        
        if not renewal_button:
            page_text = driver.page_source
            if "180 days" in page_text or "less than 180" in page_text:
                print(f"  ℹ️ [域名: {domain}] 不在续期窗口期(需少于180天)")
                return False
            print(f"  ⚠️ [域名: {domain}] 未找到续期按钮")
            driver.save_screenshot(f"renewal_button_not_found_{domain}.png")
            return False
        
        print(f"  [域名: {domain}] 点击续期按钮...")
        driver.execute_script("arguments[0].scrollIntoView(true);", renewal_button)
        time.sleep(1)
        renewal_button.click()
        time.sleep(5)
        
        # 检查是否需要确认
        try:
            confirm = wait_and_find_element(driver, By.XPATH, "//button[contains(text(), 'Confirm') or @type='submit']", timeout=3, clickable=True)
            if confirm:
                print(f"  [域名: {domain}] 点击确认...")
                confirm.click()
                time.sleep(3)
        except:
            pass
        
        # 验证结果
        time.sleep(2)
        page_source = driver.page_source.lower()
        success_keywords = ["success", "renewed", "expiration", "updated"]
        
        if any(kw in page_source for kw in success_keywords):
            print(f"  ✅ [域名: {domain}] 续期成功!")
            return True
        else:
            print(f"  ⚠️ [域名: {domain}] 续期状态未知")
            return False
            
    except Exception as e:
        print(f"  ❌ [域名: {domain}] 续期异常: {e}")
        try:
            driver.save_screenshot(f"renew_exception_{domain}.png")
        except:
            pass
        return False

def renew_account_domains(account_num, username, password, domains):
    """处理单个账户"""
    print(f"\n{'='*60}")
    print(f"[账户 {account_num}: {username}] 开始处理...")
    print(f"{'='*60}")
    
    if not domains or domains.strip() == "":
        print(f"[账户 {account_num}] 未配置域名,跳过")
        return
    
    driver = None
    try:
        print(f"[账户 {account_num}] 启动浏览器...")
        driver = setup_driver()
        
        if not login_account(driver, account_num, username, password):
            print(f"[账户 {account_num}] 登录失败,跳过")
            return
        
        domain_list = [d.strip() for d in domains.split(',') if d.strip()]
        print(f"[账户 {account_num}] 共 {len(domain_list)} 个域名: {', '.join(domain_list)}")
        
        success_count = 0
        for i, domain in enumerate(domain_list, 1):
            print(f"\n[账户 {account_num}] 处理 {i}/{len(domain_list)}: {domain}")
            if renew_single_domain(driver, account_num, domain):
                success_count += 1
            time.sleep(2)
        
        print(f"\n[账户 {account_num}] 完成: {success_count}/{len(domain_list)} 成功")
        
    except Exception as e:
        print(f"❌ [账户 {account_num}] 处理异常: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print(f"[账户 {account_num}] 浏览器已关闭")
            except:
                pass

def main():
    """主函数"""
    print("="*60)
    print("DigitalPlat 域名自动续期脚本")
    print("版本: 2025-01-30 (支持两步登录+Cloudflare)")
    print("="*60)
    
    account_index = 1
    processed_count = 0
    
    while True:
        username = os.environ.get(f'ACCOUNT_{account_index}_USERNAME')
        password = os.environ.get(f'ACCOUNT_{account_index}_PASSWORD')
        domains = os.environ.get(f'ACCOUNT_{account_index}_DOMAINS', '')
        
        if username and password:
            renew_account_domains(account_index, username, password, domains)
            processed_count += 1
            account_index += 1
            
            if os.environ.get(f'ACCOUNT_{account_index}_USERNAME'):
                print(f"\n等待5秒后处理下一个账户...")
                time.sleep(5)
        else:
            if account_index == 1:
                print("\n❌ 错误: 未找到账户配置")
                print("请在 GitHub Secrets 中设置:")
                print("  ACCOUNT_1_USERNAME (邮箱)")
                print("  ACCOUNT_1_PASSWORD (密码)")
                print("  ACCOUNT_1_DOMAINS (域名,用逗号分隔)")
            break
    
    print(f"\n{'='*60}")
    print(f"所有 {processed_count} 个账户已处理完毕")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
