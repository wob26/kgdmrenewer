#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigitalPlat 域名自动续期脚本
适配新版 DigitalPlat Domain Dashboard (2025年1月版本)
支持两步登录流程: 邮箱 -> Next -> 密码 -> Login
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
    修复网络SSL验证问题和驱动兼容性问题
    """
    # 禁用SSL证书验证,解决GitHub Actions中的网络问题
    os.environ['WDM_SSL_VERIFY'] = '0'
    
    chrome_options = Options()
    
    # 无头模式配置
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 禁用自动化检测特征
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 忽略SSL证书错误
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    
    # 稳定性配置
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    try:
        # 使用 webdriver-manager 自动管理驱动
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"❌ 创建浏览器驱动失败: {e}")
        raise

def wait_and_find_element(driver, by, value, timeout=20, clickable=False):
    """
    等待并查找页面元素
    """
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

def login_account(driver, account_num, username, password):
    """
    登录到 DigitalPlat 账户
    采用两步登录流程:
    1. 输入邮箱 -> 点击 Next
    2. 输入密码 -> 点击 Login
    """
    try:
        login_url = "https://dash.domain.digitalplat.org/auth/login"
        print(f"[账户 {account_num}] 正在打开登录页面: {login_url}")
        driver.get(login_url)
        time.sleep(4)
        
        # ========== 第一步: 输入邮箱 ==========
        print(f"[账户 {account_num}] 步骤1: 正在输入邮箱...")
        email_field = None
        
        # 尝试多种方式定位邮箱输入框
        email_selectors = [
            (By.XPATH, "//input[@placeholder='E-Mail']"),
            (By.XPATH, "//input[contains(@placeholder, 'E-Mail')]"),
            (By.XPATH, "//input[contains(@placeholder, 'mail')]"),
            (By.XPATH, "//input[@type='email']"),
            (By.NAME, "email"),
            (By.ID, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[placeholder*='mail' i]"),
            (By.XPATH, "//input[@name='identifier']"),
        ]
        
        for by, value in email_selectors:
            email_field = wait_and_find_element(driver, by, value, timeout=5)
            if email_field:
                print(f"[账户 {account_num}] ✓ 找到邮箱输入框")
                break
        
        if not email_field:
            print(f"❌ [账户 {account_num}] 未找到邮箱输入框")
            # 保存截图用于调试
            try:
                driver.save_screenshot(f"login_step1_failed_account_{account_num}.png")
                print(f"[账户 {account_num}] 已保存截图")
            except:
                pass
            return False
        
        email_field.clear()
        email_field.send_keys(username)
        time.sleep(1.5)
        
        # ========== 第二步: 点击 "Next" 按钮 ==========
        print(f"[账户 {account_num}] 步骤2: 正在点击 Next 按钮...")
        next_button = None
        
        next_selectors = [
            (By.XPATH, "//button[contains(text(), 'Next')]"),
            (By.XPATH, "//button[normalize-space()='Next']"),
            (By.XPATH, "//button[@type='submit' and contains(text(), 'Next')]"),
            (By.XPATH, "//input[@type='submit' and @value='Next']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(@class, 'submit')]"),
        ]
        
        for by, value in next_selectors:
            next_button = wait_and_find_element(driver, by, value, timeout=5, clickable=True)
            if next_button:
                # 验证按钮文本是否包含 Next
                button_text = next_button.text.strip()
                if 'Next' in button_text or button_text == '' or 'submit' in next_button.get_attribute('type').lower():
                    print(f"[账户 {account_num}] ✓ 找到 Next 按钮")
                    break
                else:
                    next_button = None
        
        if not next_button:
            print(f"❌ [账户 {account_num}] 未找到 Next 按钮")
            try:
                driver.save_screenshot(f"login_step2_failed_account_{account_num}.png")
            except:
                pass
            return False
        
        next_button.click()
        time.sleep(4)
        
        # ========== 第三步: 输入密码 ==========
        print(f"[账户 {account_num}] 步骤3: 正在输入密码...")
        password_field = None
        
        password_selectors = [
            (By.XPATH, "//input[@placeholder='Password']"),
            (By.XPATH, "//input[@type='password']"),
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ]
        
        for by, value in password_selectors:
            password_field = wait_and_find_element(driver, by, value, timeout=5)
            if password_field:
                print(f"[账户 {account_num}] ✓ 找到密码输入框")
                break
        
        if not password_field:
            print(f"❌ [账户 {account_num}] 未找到密码输入框")
            try:
                driver.save_screenshot(f"login_step3_failed_account_{account_num}.png")
            except:
                pass
            return False
        
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1.5)
        
        # ========== 第四步: 点击 "Login" 按钮 ==========
        print(f"[账户 {account_num}] 步骤4: 正在点击 Login 按钮...")
        login_button = None
        
        login_selectors = [
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//button[normalize-space()='Login']"),
            (By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]"),
            (By.XPATH, "//input[@type='submit' and @value='Login']"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ]
        
        for by, value in login_selectors:
            login_button = wait_and_find_element(driver, by, value, timeout=5, clickable=True)
            if login_button:
                button_text = login_button.text.strip()
                if 'Login' in button_text or button_text == '' or 'submit' in login_button.get_attribute('type').lower():
                    print(f"[账户 {account_num}] ✓ 找到 Login 按钮")
                    break
                else:
                    login_button = None
        
        if not login_button:
            print(f"❌ [账户 {account_num}] 未找到 Login 按钮")
            try:
                driver.save_screenshot(f"login_step4_failed_account_{account_num}.png")
            except:
                pass
            return False
        
        login_button.click()
        time.sleep(6)
        
        # ========== 第五步: 验证登录是否成功 ==========
        print(f"[账户 {account_num}] 步骤5: 验证登录状态...")
        current_url = driver.current_url
        
        # 检查URL是否跳转到仪表板或其他已登录页面
        if "login" not in current_url.lower():
            print(f"✅ [账户 {account_num}] 登录成功! 当前页面: {current_url}")
            return True
        
        # 检查是否还在登录页面（可能登录失败）
        if "login" in current_url.lower():
            # 检查是否有错误消息
            try:
                error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid') or contains(text(), 'incorrect') or contains(text(), 'wrong') or contains(text(), 'error')]")
                if error_elements:
                    print(f"❌ [账户 {account_num}] 登录失败: 用户名或密码错误")
                else:
                    print(f"❌ [账户 {account_num}] 登录失败: 仍在登录页面")
            except:
                print(f"❌ [账户 {account_num}] 登录失败: 仍在登录页面")
            
            try:
                driver.save_screenshot(f"login_failed_final_account_{account_num}.png")
            except:
                pass
            return False
        
        # 如果URL不确定，再等一会儿看看
        time.sleep(3)
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print(f"✅ [账户 {account_num}] 登录成功! 当前页面: {current_url}")
            return True
        else:
            print(f"❌ [账户 {account_num}] 登录失败，当前URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ [账户 {account_num}] 登录过程出错: {e}")
        try:
            driver.save_screenshot(f"login_exception_account_{account_num}.png")
        except:
            pass
        return False

def renew_single_domain(driver, account_num, domain):
    """
    续期单个域名
    新流程: 访问域名管理页面 -> 点击Renew标签 -> 点击Request free renewal按钮
    """
    try:
        # 构建域名管理页面URL
        domain_manage_url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        print(f"  [域名: {domain}] 正在访问管理页面...")
        driver.get(domain_manage_url)
        time.sleep(3)
        
        # 步骤1: 点击 "Renew" 标签按钮
        print(f"  [域名: {domain}] 正在查找 Renew 标签...")
        
        # 尝试多种选择器查找Renew按钮
        renew_button = None
        selectors = [
            "//button[contains(text(), 'Renew')]",
            "//button[contains(@class, 'tab') and contains(text(), 'Renew')]",
            "//a[contains(text(), 'Renew')]",
            "//*[contains(@class, 'tab-button') and contains(text(), 'Renew')]",
            "//*[@role='tab' and contains(text(), 'Renew')]",
            "//button[normalize-space()='Renew']",
        ]
        
        for selector in selectors:
            renew_button = wait_and_find_element(driver, By.XPATH, selector, timeout=5, clickable=True)
            if renew_button:
                break
        
        if not renew_button:
            print(f"  ⚠️ [域名: {domain}] 未找到 Renew 标签按钮")
            try:
                driver.save_screenshot(f"renew_tab_not_found_{domain}.png")
            except:
                pass
            return False
        
        print(f"  [域名: {domain}] 正在点击 Renew 标签...")
        driver.execute_script("arguments[0].scrollIntoView(true);", renew_button)
        time.sleep(1)
        renew_button.click()
        time.sleep(3)
        
        # 步骤2: 点击 "Request free renewal" 按钮
        print(f"  [域名: {domain}] 正在查找 Request free renewal 按钮...")
        
        renewal_button = None
        selectors = [
            "//button[contains(text(), 'Request free renewal')]",
            "//button[contains(text(), 'Free renewal')]",
            "//button[contains(text(), 'Free Renewal')]",
            "//*[contains(@class, 'button') and contains(text(), 'Request')]",
            "//button[contains(., 'Request') and contains(., 'free')]",
        ]
        
        for selector in selectors:
            renewal_button = wait_and_find_element(driver, By.XPATH, selector, timeout=5, clickable=True)
            if renewal_button:
                break
        
        if not renewal_button:
            # 检查是否显示了续期窗口提示
            page_text = driver.page_source
            if "Available when less than 180 days remain" in page_text or "180 days" in page_text:
                print(f"  ℹ️ [域名: {domain}] 域名不在免费续期窗口期内(需要剩余天数少于180天)")
                return False
            else:
                print(f"  ⚠️ [域名: {domain}] 未找到 Request free renewal 按钮")
                try:
                    driver.save_screenshot(f"renewal_button_not_found_{domain}.png")
                except:
                    pass
                return False
        
        print(f"  [域名: {domain}] 正在点击 Request free renewal 按钮...")
        driver.execute_script("arguments[0].scrollIntoView(true);", renewal_button)
        time.sleep(1)
        renewal_button.click()
        time.sleep(4)
        
        # 步骤3: 检查是否需要最终确认
        try:
            confirm_button = wait_and_find_element(driver, By.XPATH, "//button[@type='submit' or contains(text(), 'Confirm') or contains(text(), 'Yes')]", timeout=5, clickable=True)
            if confirm_button:
                print(f"  [域名: {domain}] 正在点击确认按钮...")
                confirm_button.click()
                time.sleep(3)
        except:
            pass
        
        # 步骤4: 验证续期是否成功
        time.sleep(2)
        page_source = driver.page_source.lower()
        
        success_keywords = [
            "success", "成功", "renewed", "已续期",
            "expiration date", "到期日期", "updated"
        ]
        
        is_success = any(keyword in page_source for keyword in success_keywords)
        
        if is_success:
            print(f"  ✅ [域名: {domain}] 续期成功!")
            return True
        else:
            if "error" in page_source or "fail" in page_source:
                print(f"  ❌ [域名: {domain}] 续期失败,页面显示错误")
            else:
                print(f"  ⚠️ [域名: {domain}] 续期状态未知")
            return False
            
    except Exception as e:
        print(f"  ❌ [域名: {domain}] 续期过程出错: {e}")
        try:
            driver.save_screenshot(f"renew_exception_{domain}.png")
        except:
            pass
        return False

def renew_account_domains(account_num, username, password, domains):
    """
    处理单个账户的所有域名续期
    """
    print(f"\n{'='*60}")
    print(f"[账户 {account_num}: {username}] 开始处理...")
    print(f"{'='*60}")
    
    if not domains or domains.strip() == "":
        print(f"[账户 {account_num}] 未配置任何域名,跳过")
        return
    
    driver = None
    try:
        # 创建浏览器实例
        print(f"[账户 {account_num}] 正在启动浏览器...")
        driver = setup_driver()
        
        # 登录账户
        if not login_account(driver, account_num, username, password):
            print(f"[账户 {account_num}] 登录失败,跳过此账户")
            return
        
        # 解析域名列表
        domain_list = [d.strip() for d in domains.split(',') if d.strip()]
        print(f"[账户 {account_num}] 共需处理 {len(domain_list)} 个域名: {', '.join(domain_list)}")
        
        # 逐个续期域名
        success_count = 0
        for i, domain in enumerate(domain_list, 1):
            print(f"\n[账户 {account_num}] 正在处理第 {i}/{len(domain_list)} 个域名: {domain}")
            if renew_single_domain(driver, account_num, domain):
                success_count += 1
            time.sleep(2)
        
        print(f"\n[账户 {account_num}] 处理完毕: 成功 {success_count}/{len(domain_list)} 个域名")
        
    except WebDriverException as e:
        print(f"❌ [账户 {account_num}] 浏览器驱动错误: {e}")
        print("提示: 这可能是Chrome版本不兼容导致的")
    except Exception as e:
        print(f"❌ [账户 {account_num}] 处理过程发生严重错误: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print(f"[账户 {account_num}] 浏览器已关闭")
            except:
                pass

def main():
    """
    主函数: 读取环境变量并处理所有账户
    """
    print("="*60)
    print("DigitalPlat 域名自动续期脚本")
    print("适配版本: 2025年1月 (支持两步登录)")
    print("="*60)
    
    account_index = 1
    processed_count = 0
    
    while True:
        # 读取环境变量
        username = os.environ.get(f'ACCOUNT_{account_index}_USERNAME')
        password = os.environ.get(f'ACCOUNT_{account_index}_PASSWORD')
        domains = os.environ.get(f'ACCOUNT_{account_index}_DOMAINS', '')
        
        if username and password:
            renew_account_domains(account_index, username, password, domains)
            processed_count += 1
            account_index += 1
            
            # 账户之间的间隔
            if os.environ.get(f'ACCOUNT_{account_index}_USERNAME'):
                print(f"\n等待5秒后处理下一个账户...")
                time.sleep(5)
        else:
            if account_index == 1:
                print("\n❌ 错误: 未找到任何账户配置")
                print("请在 GitHub Secrets 中添加以下变量:")
                print("  ACCOUNT_1_USERNAME: 第一个账户的邮箱")
                print("  ACCOUNT_1_PASSWORD: 第一个账户的密码")
                print("  ACCOUNT_1_DOMAINS: 第一个账户的域名列表(用逗号分隔)")
                print("\n如有多个账户,继续添加 ACCOUNT_2_USERNAME, ACCOUNT_2_PASSWORD 等...")
            break
    
    print(f"\n{'='*60}")
    print(f"所有 {processed_count} 个账户均已处理完毕")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
