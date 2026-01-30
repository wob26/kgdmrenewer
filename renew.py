#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_driver_simple():
    """最简单的浏览器设置"""
    options = uc.ChromeOptions()
    
    # 关键：不使用headless
    # options.add_argument('--headless')  # 注释掉，让xvfb处理显示
    
    # 基础设置
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # 反检测
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        print("🚀 启动浏览器...")
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"❌ 浏览器启动失败: {e}")
        # 尝试更简单的设置
        try:
            driver = uc.Chrome()
            return driver
        except Exception as e2:
            print(f"❌ 简单设置也失败: {e2}")
            return None

def wait_for_element(driver, selector, by=By.XPATH, timeout=30):
    """等待元素出现"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        return None

def save_screenshot(driver, name):
    """保存截图"""
    try:
        filename = f"debug_{name}.png"
        driver.save_screenshot(filename)
        print(f"📸 截图: {filename}")
        return True
    except Exception as e:
        print(f"⚠️ 截图失败: {e}")
        return False

def try_login_simple(driver, username, password, account_num):
    """简单登录尝试"""
    try:
        print(f"\n🔐 尝试登录账户 {account_num}...")
        
        # 访问登录页
        driver.get("https://dash.domain.digitalplat.org/auth/login")
        time.sleep(10)  # 给Cloudflare验证时间
        
        save_screenshot(driver, f"acc{account_num}_page")
        
        # 检查页面内容
        page_source = driver.page_source.lower()
        if "verifying" in page_source or "cloudflare" in page_source:
            print("🛡️ Cloudflare验证中，等待...")
            time.sleep(15)  # 再等一会
        
        # 尝试查找邮箱输入框
        email_selectors = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
        ]
        
        email_field = None
        for by, selector in email_selectors:
            try:
                email_field = driver.find_element(by, selector)
                if email_field:
                    print(f"✅ 找到邮箱输入框: {selector}")
                    break
            except:
                continue
        
        if not email_field:
            print("❌ 未找到邮箱输入框")
            save_screenshot(driver, f"acc{account_num}_no_email")
            return False
        
        # 输入邮箱
        email_field.clear()
        email_field.send_keys(username)
        time.sleep(2)
        
        # 尝试点击Next或提交
        try:
            # 查找按钮
            next_buttons = [
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), '下一步')]",
                "//button[@type='submit']",
            ]
            
            for xpath in next_buttons:
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    if button:
                        button.click()
                        print(f"✅ 点击按钮: {xpath}")
                        break
                except:
                    continue
        except:
            pass
        
        time.sleep(5)
        
        # 查找密码框
        pwd_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ]
        
        pwd_field = None
        for by, selector in pwd_selectors:
            try:
                pwd_field = driver.find_element(by, selector)
                if pwd_field:
                    print(f"✅ 找到密码输入框: {selector}")
                    break
            except:
                continue
        
        if not pwd_field:
            print("❌ 未找到密码输入框")
            save_screenshot(driver, f"acc{account_num}_no_password")
            return False
        
        # 输入密码
        pwd_field.clear()
        pwd_field.send_keys(password)
        time.sleep(2)
        
        # 尝试点击登录
        try:
            login_buttons = [
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), '登录')]",
                "//input[@type='submit']",
            ]
            
            for xpath in login_buttons:
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    if button:
                        button.click()
                        print(f"✅ 点击登录: {xpath}")
                        break
                except:
                    continue
        except:
            pass
        
        # 等待登录结果
        time.sleep(10)
        save_screenshot(driver, f"acc{account_num}_after_login")
        
        # 检查是否登录成功
        current_url = driver.current_url.lower()
        if "login" not in current_url and "auth" not in current_url:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 登录可能失败")
            return False
            
    except Exception as e:
        print(f"❌ 登录异常: {str(e)[:200]}")
        save_screenshot(driver, f"acc{account_num}_error")
        return False

def renew_domains(driver, domains):
    """续期域名"""
    success_count = 0
    
    for domain in domains:
        try:
            print(f"\n🌐 处理: {domain}")
            
            # 访问域名页面
            url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
            driver.get(url)
            time.sleep(5)
            
            # 查找Renew相关按钮
            try:
                # 先找Renew标签页
                renew_tab = driver.find_element(By.XPATH, "//button[contains(@class, 'tab-btn') and contains(., 'Renew')]")
                if renew_tab:
                    renew_tab.click()
                    time.sleep(2)
            except:
                pass
            
            # 找Renew按钮
            try:
                renew_btn = driver.find_element(By.XPATH, "//button[contains(., 'Renew') and not(contains(@class, 'tab-btn'))]")
                if renew_btn:
                    renew_btn.click()
                    time.sleep(3)
                    
                    # 找免费续期按钮
                    free_btn = driver.find_element(By.XPATH, "//button[contains(., 'Request free renewal')]")
                    if free_btn:
                        free_btn.click()
                        time.sleep(2)
                        print(f"✅ {domain} 续期请求已发送")
                        success_count += 1
                    else:
                        print(f"ℹ️ {domain} 未找到免费续期按钮")
                else:
                    print(f"ℹ️ {domain} 未找到Renew按钮")
            except Exception as e:
                print(f"⚠️ {domain} 处理异常: {e}")
                
        except Exception as e:
            print(f"❌ {domain} 失败: {str(e)[:100]}")
    
    return success_count

def main():
    """主函数"""
    print("=" * 60)
    print("DPDNS 域名自动续期 (简化版)")
    print("=" * 60)
    
    driver = None
    try:
        # 初始化浏览器
        driver = setup_driver_simple()
        if not driver:
            print("❌ 无法启动浏览器，退出")
            return
        
        account_num = 1
        while True:
            # 获取账户信息
            username = os.environ.get(f'ACCOUNT_{account_num}_USERNAME')
            password = os.environ.get(f'ACCOUNT_{account_num}_PASSWORD')
            domains_str = os.environ.get(f'ACCOUNT_{account_num}_DOMAINS', '')
            
            if not username or not password:
                break
            
            print(f"\n{'='*50}")
            print(f"账户 {account_num}")
            print(f"{'='*50}")
            
            # 尝试登录
            if try_login_simple(driver, username, password, account_num):
                print("🔓 登录成功，处理域名...")
                
                # 处理域名
                domains = [d.strip() for d in domains_str.split(',') if d.strip()]
                if domains:
                    success = renew_domains(driver, domains)
                    print(f"\n📊 成功续期: {success}/{len(domains)} 个域名")
                else:
                    print("⚠️ 未配置域名")
            else:
                print("⏭️ 登录失败，跳过")
            
            account_num += 1
            
            # 账户间等待
            if account_num > 1:
                time.sleep(3)
        
        print(f"\n✨ 处理完成，共处理 {account_num-1} 个账户")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print("🛑 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    main()