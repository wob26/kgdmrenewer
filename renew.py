#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import asyncio
from playwright.async_api import async_playwright

async def setup_browser():
    """使用Playwright设置浏览器"""
    playwright = await async_playwright().start()
    
    # 使用Chromium，非headless模式
    browser = await playwright.chromium.launch(
        headless=False,  # 非headless
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--window-size=1920,1080',
            '--start-maximized',
            '--disable-notifications',
        ]
    )
    
    # 创建上下文，模拟真实浏览器
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
        permissions=['notifications'],
        bypass_csp=True,
        ignore_https_errors=True,
        java_script_enabled=True,
    )
    
    # 添加额外的反检测脚本
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    """)
    
    page = await context.new_page()
    page.set_default_timeout(60000)
    
    return playwright, browser, context, page

async def save_screenshot(page, name):
    """保存截图"""
    try:
        filename = f"debug_{name}.png"
        await page.screenshot(path=filename, full_page=True)
        print(f"📸 截图保存: {filename}")
        return True
    except Exception as e:
        print(f"⚠️ 截图失败: {e}")
        return False

async def login_account(page, username, password, acc_idx):
    """登录账户"""
    try:
        print(f"\n🔐 开始登录账户 {acc_idx}...")
        
        # 访问登录页
        await page.goto("https://dash.domain.digitalplat.org/auth/login", wait_until="networkidle")
        await asyncio.sleep(8 + random.random() * 2)
        
        # 初始截图
        await save_screenshot(page, f"acc{acc_idx}_initial")
        
        # 检查是否有Cloudflare验证
        if "verifying" in (await page.content()).lower() or "cloudflare" in (await page.content()).lower():
            print("🛡️ 检测到Cloudflare验证，等待中...")
            await asyncio.sleep(15)  # 给验证时间
            await save_screenshot(page, f"acc{acc_idx}_cloudflare")
        
        # 1. 查找并输入邮箱
        print("📧 输入邮箱...")
        
        # 尝试多种选择器
        email_selectors = [
            '#email',
            'input[type="email"]',
            'input[name="email"]',
            '[placeholder*="email" i]',
            '[placeholder*="邮箱" i]',
        ]
        
        email_found = False
        for selector in email_selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                await page.fill(selector, username)
                email_found = True
                print(f"✅ 找到并填写邮箱输入框: {selector}")
                break
            except:
                continue
        
        if not email_found:
            print("❌ 未找到邮箱输入框")
            await save_screenshot(page, f"acc{acc_idx}_no_email")
            return False
        
        await asyncio.sleep(1 + random.random())
        
        # 2. 点击Next按钮
        print("🔄 点击下一步...")
        
        # 尝试点击Next按钮
        next_clicked = False
        next_selectors = [
            'button:has-text("Next")',
            'button:has-text("下一步")',
            'input[type="submit"]',
            'button[type="submit"]',
        ]
        
        for selector in next_selectors:
            try:
                await page.click(selector, timeout=5000)
                next_clicked = True
                print(f"✅ 点击: {selector}")
                break
            except:
                continue
        
        if not next_clicked:
            print("⚠️ 尝试按回车键...")
            await page.keyboard.press('Enter')
        
        await asyncio.sleep(6 + random.random() * 2)
        await save_screenshot(page, f"acc{acc_idx}_after_email")
        
        # 3. 查找并输入密码
        print("🔑 输入密码...")
        
        pwd_selectors = [
            '#password',
            'input[type="password"]',
            'input[name="password"]',
            '[placeholder*="password" i]',
            '[placeholder*="密码" i]',
        ]
        
        pwd_found = False
        for selector in pwd_selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                await page.fill(selector, password)
                pwd_found = True
                print(f"✅ 找到并填写密码输入框: {selector}")
                break
            except:
                continue
        
        if not pwd_found:
            print("❌ 未找到密码输入框")
            await save_screenshot(page, f"acc{acc_idx}_no_password")
            return False
        
        await asyncio.sleep(2 + random.random())
        
        # 4. 处理验证码
        print("🛡️ 等待验证码...")
        await asyncio.sleep(10)
        await save_screenshot(page, f"acc{acc_idx}_before_login")
        
        # 5. 点击登录按钮
        print("🚀 尝试登录...")
        
        login_clicked = False
        login_selectors = [
            'button:has-text("Login")',
            'button:has-text("登录")',
            'input[value*="Login" i]',
            'input[value*="登录" i]',
        ]
        
        for selector in login_selectors:
            try:
                await page.click(selector, timeout=10000)
                login_clicked = True
                print(f"✅ 点击登录: {selector}")
                break
            except:
                continue
        
        if not login_clicked:
            print("⚠️ 尝试在密码框按回车...")
            await page.keyboard.press('Enter')
        
        # 6. 等待登录完成
        await asyncio.sleep(12 + random.random() * 3)
        await save_screenshot(page, f"acc{acc_idx}_after_login")
        
        # 7. 检查是否登录成功
        current_url = page.url.lower()
        if "login" not in current_url and "auth" not in current_url:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 可能登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 登录过程异常: {str(e)[:150]}")
        await save_screenshot(page, f"acc{acc_idx}_error")
        return False

async def renew_domain(page, domain):
    """续期域名"""
    try:
        print(f"\n🌐 处理域名: {domain}")
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(6 + random.random() * 2)
        
        await save_screenshot(page, f"domain_{domain.replace('.', '_')}_initial")
        
        # 点击Renew标签
        print("  📍 查找Renew标签页...")
        
        try:
            # 点击Renew标签按钮
            await page.click('button.tab-btn:has-text("Renew")', timeout=10000)
            print("  ✅ 已切换到Renew标签页")
            await asyncio.sleep(3)
        except:
            print("  ℹ️ Renew标签可能已激活")
        
        # 点击Renew按钮
        try:
            renew_button = await page.wait_for_selector('button:has-text("Renew"):not(.tab-btn)', timeout=10000)
            await renew_button.click()
            print("  ✅ 点击Renew按钮")
            await asyncio.sleep(3)
            
            # 点击免费续期按钮
            try:
                free_button = await page.wait_for_selector('button:has-text("Request free renewal")', timeout=10000)
                await free_button.click()
                print(f"  ✅ {domain} 续期请求已发送")
                await asyncio.sleep(3)
                await save_screenshot(page, f"domain_{domain.replace('.', '_')}_success")
                return True
            except:
                print(f"  ℹ️ {domain} 未找到免费续期按钮")
                return False
                
        except:
            print(f"  ℹ️ {domain} 未找到Renew按钮或已续期")
            return False
            
    except Exception as e:
        print(f"❌ {domain} 处理失败: {str(e)[:100]}")
        await save_screenshot(page, f"domain_{domain.replace('.', '_')}_error")
        return False

async def main_async():
    """异步主函数"""
    print("=" * 60)
    print("DPDNS 域名自动续期脚本 (Playwright版本)")
    print("=" * 60)
    
    idx = 1
    playwright = browser = context = page = None
    
    try:
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
            
            try:
                # 初始化浏览器
                playwright, browser, context, page = await setup_browser()
                
                # 登录
                if await login_account(page, user, pwd, idx):
                    print("🔓 登录成功，开始检查域名...")
                    # 处理域名
                    domains = [d.strip() for d in doms.split(',') if d.strip()]
                    for domain in domains:
                        await renew_domain(page, domain)
                        await asyncio.sleep(3 + random.random() * 2)
                else:
                    print("⏭️ 登录失败，跳过此账户")
                    
            except Exception as e:
                print(f"❌ 账户 {idx} 处理异常: {e}")
                
            finally:
                # 清理当前账户的浏览器会话
                if page:
                    await page.close()
                if context:
                    await context.close()
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()
            
            idx += 1
            if idx > 1:
                await asyncio.sleep(5 + random.random() * 3)
                
    except Exception as e:
        print(f"❌ 主程序异常: {e}")
        
    finally:
        # 最终清理
        try:
            if page: await page.close()
            if context: await context.close()
            if browser: await browser.close()
            if playwright: await playwright.stop()
        except:
            pass
    
    print("\n✨ 脚本执行完成！")

def main():
    """同步入口函数"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()