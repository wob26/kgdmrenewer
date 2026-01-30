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
from selenium.webdriver.common.keys import Keys

def get_chrome_version():
    """获取Chrome版本"""
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        version_str = output.strip().split()[-1]
        return int(version_str.split('.')[0])
    except:
        return 120  # 默认版本

def setup_driver():
    """设置浏览器驱动 - 修复参数问题"""
    options = uc.ChromeOptions()
    
    # 基础选项
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # undetected_chromedriver 不需要 excludeSwitches 参数
    # 只需要基本反检测参数
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # 用户代理和窗口大小
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # 添加一些额外的参数来避免检测
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # 语言设置
    options.add_argument('--lang=en-US,en;q=0.9')
    
    try:
        version = get_chrome_version()
        print(f"🚀 使用 Chrome 版本: {version}")
        
        # 使用 undetected_chromedriver 的简化配置
        driver = uc.Chrome(
            options=options,
            version_main=version,
            headless=True,  # 确保 headless 模式
            suppress_welcome=True
        )
        
        # 隐藏WebDriver特征 - 使用JavaScript方式
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
        
        driver.set_page_load_timeout(45)
        driver.set_script_timeout(30)
        
        return driver
        
    except Exception as e:
        print(f"❌ 浏览器初始化失败: {e}")
        # 尝试更简单的配置
        print("🔄 尝试简化配置...")
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e2:
            print(f"❌ 简化配置也失败: {e2}")
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
        time.sleep(0.5)
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))
        return True
    except Exception as e:
        print(f"⚠️ 输入失败，尝试JS方式: {e}")
        try:
            driver = element.parent
            driver.execute_script(f"arguments[0].value = '{text}';", element)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
            return True
        except:
            return False

def wait_and_click(driver, selector, by=By.XPATH, timeout=15, description=""):
    """等待并点击元素"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        
        # 滚动到元素
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.3 + random.random() * 0.3)
        
        # 尝试JavaScript点击
        try:
            driver.execute_script("arguments[0].click();", element)
        except:
            element.click()
            
        print(f"✅ 点击: {description or selector[:50]}")
        time.sleep(1 + random.random() * 0.5)
        return True
        
    except Exception as e:
        print(f"⚠️ 点击失败 {description or selector[:50]}: {str(e)[:80]}")
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
            (By.CSS_SELECTOR, "input[name='email']"),
        ]
        
        email_field = find_element_multi_strategy(driver, email_selectors, 20)
        if not email_field:
            print("❌ 未找到邮箱输入框")
            save_screenshot(driver, f"acc{acc_idx}_no_email")
            return False
            
        if not human_type(email_field, username):
            print("❌ 邮箱输入失败")
            return False
            
        time.sleep(1 + random.random())
        
        # 2. 点击Next按钮
        print("🔄 点击下一步...")
        next_selectors = [
            "//button[contains(text(), 'Next')]",
            "//button[contains(text(), '下一步')]",
            "//button[text()='Next']",
            "//input[@type='submit']",
            "//button[@type='submit']",
        ]
        
        clicked = False
        for selector in next_selectors:
            if wait_and_click(driver, selector, timeout=8, description="Next按钮"):
                clicked = True
                break
                
        if not clicked:
            print("⚠️ 尝试回车继续...")
            email_field.send_keys(Keys.RETURN)
            
        time.sleep(6 + random.random() * 2)
        save_screenshot(driver, f"acc{acc_idx}_after_email")
        
        # 3. 查找并输入密码
        print("🔑 输入密码...")
        pwd_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.XPATH, "//input[@type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
        ]
        
        pwd_field = find_element_multi_strategy(driver, pwd_selectors, 20)
        if not pwd_field:
            print("❌ 未找到密码输入框")
            save_screenshot(driver, f"acc{acc_idx}_no_password")
            return False
            
        if not human_type(pwd_field, password):
            print("❌ 密码输入失败")
            return False
            
        time.sleep(2 + random.random())
        
        # 4. 处理验证码（如果有）
        print("🛡️ 等待验证码...")
        time.sleep(8)  # 给验证码足够时间加载
        save_screenshot(driver, f"acc{acc_idx}_before_login")
        
        # 5. 点击登录按钮
        print("🚀 尝试登录...")
        login_selectors = [
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), '登录')]",
            "//button[@type='submit' and not(contains(text(), 'Next'))]",
            "//input[@type='submit' and contains(@value, 'Login')]",
            "//input[@type='submit' and contains(@value, '登录')]",
        ]
        
        login_clicked = False
        for selector in login_selectors:
            if wait_and_click(driver, selector, timeout=15, description="登录按钮"):
                login_clicked = True
                break
                
        if not login_clicked:
            print("⚠️ 尝试回车登录...")
            pwd_field.send_keys(Keys.RETURN)
            
        # 6. 等待登录完成
        time.sleep(10 + random.random() * 3)
        save_screenshot(driver, f"acc{acc_idx}_after_login")
        
        # 7. 验证登录成功
        current_url = driver.current_url.lower()
        if "login" not in current_url and "auth" not in current_url:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 可能登录失败，当前URL:", driver.current_url)
            # 检查错误信息
            try:
                error_selectors = [
                    (By.CSS_SELECTOR, ".error"),
                    (By.CSS_SELECTOR, ".alert-danger"),
                    (By.CSS_SELECTOR, ".text-danger"),
                    (By.CSS_SELECTOR, ".alert"),
                    (By.XPATH, "//*[contains(text(), '错误') or contains(text(), 'Error') or contains(text(), '验证')]"),
                ]
                
                for by, selector in error_selectors:
                    try:
                        errors = driver.find_elements(by, selector)
                        for error in errors[:2]:
                            if error.text.strip():
                                print(f"⚠️ 页面提示: {error.text[:100]}")
                    except:
                        continue
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
        time.sleep(7 + random.random() * 2)
        
        # 首先截图查看页面结构
        save_screenshot(driver, f"domain_{domain.replace('.', '_')}_initial")
        
        # 根据你提供的HTML结构，找到Renew标签页
        print("  📍 查找Renew标签页...")
        
        # 方法1: 直接点击Renew标签按钮
        renew_tab_clicked = wait_and_click(driver,
            "//button[contains(@class, 'tab-btn') and contains(., 'Renew')]",
            timeout=15,
            description="Renew标签")
            
        if renew_tab_clicked:
            print("  ✅ 已切换到Renew标签页")
            time.sleep(3)
            
            # 现在查找Renew按钮
            renew_btn_clicked = wait_and_click(driver,
                "//button[contains(., 'Renew') and not(contains(@class, 'tab-btn'))]",
                timeout=15,
                description="Renew按钮")
                
            if renew_btn_clicked:
                time.sleep(3)
                
                # 查找免费续期按钮
                free_renew_clicked = wait_and_click(driver,
                    "//button[contains(., 'Request free renewal') or contains(., '免费续期') or contains(., 'free renewal')]",
                    timeout=15,
                    description="免费续期按钮")
                    
                if free_renew_clicked:
                    print(f"  ✅ {domain} 续期请求已发送")
                    time.sleep(3)
                    save_screenshot(driver, f"domain_{domain.replace('.', '_')}_success")
                    return True
                else:
                    print(f"  ℹ️ {domain} 未找到免费续期按钮")
            else:
                print(f"  ℹ️ {domain} 未找到Renew按钮")
        else:
            print(f"  ℹ️ {domain} 可能已经是Renew页面或标签结构不同")
            
            # 方法2: 直接在当前页面查找Renew按钮
            renew_btn_clicked = wait_and_click(driver,
                "//button[contains(., 'Renew')]",
                timeout=10,
                description="Renew按钮(直接)")
                
            if renew_btn_clicked:
                time.sleep(3)
                
                # 查找免费续期按钮
                free_renew_clicked = wait_and_click(driver,
                    "//button[contains(., 'Request free renewal')]",
                    timeout=10,
                    description="免费续期按钮")
                    
                if free_renew_clicked:
                    print(f"  ✅ {domain} 续期请求已发送")
                    time.sleep(3)
                    return True
            
            print(f"  ℹ️ {domain} 可能暂不支持续期")
            
        save_screenshot(driver, f"domain_{domain.replace('.', '_')}_end")
        return False
            
    except Exception as e:
        print(f"❌ {domain} 处理失败: {str(e)[:100]}")
        save_screenshot(driver, f"domain_{domain.replace('.', '_')}_error")
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