#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_chrome_version():
    """获取Chrome版本"""
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        return int(output.strip().split()[-1].split('.')[0])
    except:
        return 120  # 默认版本

def setup_driver():
    """设置浏览器驱动"""
    options = uc.ChromeOptions()
    
    # 基础选项
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # 反检测选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 用户代理和窗口大小
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1920,1080')
    
    # 防止指纹识别
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "useAutomationExtension": False,
        "excludeSwitches": ["enable-automation"]
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        version = get_chrome_version()
        print(f"🚀 使用 Chrome 版本: {version}")
        
        driver = uc.Chrome(
            options=options,
            version_main=version,
            driver_executable_path=None
        )
        
        # 隐藏WebDriver特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            '''
        })
        
        driver.set_page_load_timeout(45)
        driver.set_script_timeout(30)
        return driver
        
    except Exception as e:
        print(f"❌ 浏览器初始化失败: {e}")
        raise

def save_screenshot(driver, name):
    """保存截图"""
    try:
        filename = f"debug_{name}.png"
        driver.save_screenshot(filename)
        print(f"📸 截图保存: {filename}")
        return True
    except Exception as e:
        print(f"⚠️ 截图失败: {e}")
        return False

def human_type(element, text):
    """模拟人类输入"""
    try:
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    except:
        # 如果普通方式失败，使用JavaScript
        from selenium.webdriver.common.keys import Keys
        element.clear()
        element.send_keys(text)

def wait_and_click(driver, selector, by=By.XPATH, timeout=15, description=""):
    """等待并点击元素"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        
        # 滚动到元素
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5 + random.random())
        
        # 尝试JavaScript点击
        try:
            driver.execute_script("arguments[0].click();", element)
        except:
            element.click()
            
        print(f"✅ 点击: {description or selector}")
        time.sleep(1 + random.random())
        return True
        
    except Exception as e:
        print(f"⚠️ 点击失败 {description or selector}: {str(e)[:100]}")
        return False

def find_element_multi_strategy(driver, selectors_list, timeout=10):
    """多策略查找元素"""
    for by, selector in selectors_list:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"🔍 找到元素: {by}={selector}")
            return element
        except:
            continue
    return None

def login_account(driver, username, password, acc_idx):
    """登录账户"""
    try:
        print(f"\n🔐 开始登录账户 {acc_idx}...")
        
        # 访问登录页
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        time.sleep(8 + random.random() * 2)
        
        # 初始截图
        save_screenshot(driver, f"acc{acc_idx}_initial")
        
        # 1. 查找并输入邮箱
        print("📧 输入邮箱...")
        email_selectors = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@type='email']"),
            (By.CSS_SELECTOR, "input.email-input"),
        ]
        
        email_field = find_element_multi_strategy(driver, email_selectors, 15)
        if not email_field:
            print("❌ 未找到邮箱输入框")
            save_screenshot(driver, f"acc{acc_idx}_no_email")
            return False
            
        human_type(email_field, username)
        time.sleep(1)
        
        # 2. 点击Next按钮
        print("🔄 点击下一步...")
        next_clicked = wait_and_click(driver, 
            "//button[contains(text(), 'Next') or contains(text(), '下一步')]", 
            description="Next按钮")
        
        if not next_clicked:
            # 尝试按回车
            print("⚠️ 尝试回车继续...")
            from selenium.webdriver.common.keys import Keys
            email_field.send_keys(Keys.RETURN)
            
        time.sleep(5 + random.random() * 3)
        save_screenshot(driver, f"acc{acc_idx}_after_email")
        
        # 3. 查找并输入密码
        print("🔑 输入密码...")
        pwd_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.XPATH, "//input[@type='password']"),
        ]
        
        pwd_field = find_element_multi_strategy(driver, pwd_selectors, 15)
        if not pwd_field:
            print("❌ 未找到密码输入框")
            save_screenshot(driver, f"acc{acc_idx}_no_password")
            return False
            
        human_type(pwd_field, password)
        time.sleep(2)
        
        # 4. 处理验证码（如果有）
        print("🛡️ 等待验证码...")
        time.sleep(10)  # 给验证码足够时间加载
        save_screenshot(driver, f"acc{acc_idx}_before_login")
        
        # 5. 点击登录按钮
        print("🚀 尝试登录...")
        login_clicked = wait_and_click(driver,
            "//button[contains(text(), 'Login') or contains(text(), '登录') or @type='submit']",
            timeout=20,
            description="登录按钮")
            
        if not login_clicked:
            # 尝试在密码框按回车
            print("⚠️ 尝试回车登录...")
            from selenium.webdriver.common.keys import Keys
            pwd_field.send_keys(Keys.RETURN)
            
        # 6. 等待登录完成
        time.sleep(12 + random.random() * 3)
        save_screenshot(driver, f"acc{acc_idx}_after_login")
        
        # 7. 验证登录成功
        current_url = driver.current_url.lower()
        if "login" not in current_url and "auth" not in current_url:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 可能登录失败")
            # 检查错误信息
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .text-danger, .alert")
                for error in error_elements[:3]:  # 只看前3个
                    if error.text.strip():
                        print(f"⚠️ 页面提示: {error.text[:80]}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ 登录过程异常: {str(e)[:150]}")
        save_screenshot(driver, f"acc{acc_idx}_error")
        return False

def renew_domain(driver, domain):
    """续期域名"""
    try:
        print(f"\n🌐 处理域名: {domain}")
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        driver.get(url)
        time.sleep(6 + random.random() * 2)
        
        # 查找Renew按钮
        renew_found = wait_and_click(driver,
            "//button[contains(., 'Renew') or contains(., '续费')] | //a[contains(., 'Renew')]",
            timeout=15,
            description="Renew按钮")
            
        if not renew_found:
            print(f"  ℹ️ {domain} 未找到Renew按钮")
            return False
            
        time.sleep(4)
        
        # 查找免费续期按钮
        free_renew_found = wait_and_click(driver,
            "//button[contains(., 'Request free renewal') or contains(., '免费续期')]",
            timeout=15,
            description="免费续期按钮")
            
        if free_renew_found:
            print(f"  ✅ {domain} 续期请求已发送")
            time.sleep(3)
            return True
        else:
            print(f"  ℹ️ {domain} 可能暂不支持免费续期")
            return False
            
    except Exception as e:
        print(f"❌ {domain} 处理失败: {str(e)[:100]}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("DPDNS 域名自动续期脚本")
    print("=" * 60)
    
    idx = 1
    while True:
        # 从环境变量读取账户信息
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if not user or not pwd:
            print(f"\n📊 共处理了 {idx-1} 个账户")
            break
            
        print(f"\n{'='*50}")
        print(f"账户 {idx}: {user}")
        print(f"{'='*50}")
        
        driver = None
        try:
            # 初始化浏览器
            driver = setup_driver()
            
            # 登录
            if login_account(driver, user, pwd, idx):
                print("🔓 登录成功，开始检查域名...")
                # 处理域名
                domains = [d.strip() for d in doms.split(',') if d.strip()]
                for domain in domains:
                    renew_domain(driver, domain)
                    time.sleep(3 + random.random() * 2)
            else:
                print("⏭️ 登录失败，跳过此账户")
                
        except Exception as e:
            print(f"❌ 账户 {idx} 处理异常: {e}")
            
        finally:
            # 清理浏览器
            if driver:
                try:
                    driver.quit()
                    print(f"🛑 浏览器已关闭")
                except:
                    pass
        
        idx += 1
        if idx > 1:  # 账户间等待
            time.sleep(5 + random.random() * 3)
    
    print("\n✨ 脚本执行完成！")

if __name__ == "__main__":
    main()