#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import json
import asyncio
from playwright.async_api import async_playwright
import cloudscraper
import requests

def setup_scraper():
    """使用cloudscraper绕过Cloudflare"""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    return scraper

async def setup_stealth_browser():
    """设置更隐密的浏览器"""
    playwright = await async_playwright().start()
    
    # 使用更真实的浏览器参数
    browser = await playwright.chromium.launch(
        headless=True,  # 保持headless
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-web-security',
            '--disable-features=BlockInsecurePrivateNetworkRequests',
            '--disable-features=LazyFrameLoading',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--allow-running-insecure-content',
            '--disable-notifications',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-component-update',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-translate',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-zygote',
            '--disable-software-rasterizer',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-crash-reporter',
            '--disable-oopr-debug-crash-dump',
            '--window-size=1920,1080',
        ]
    )
    
    # 更复杂的上下文设置
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
        permissions=[],
        bypass_csp=True,
        ignore_https_errors=True,
        java_script_enabled=True,
        has_touch=False,
        is_mobile=False,
        color_scheme='light',
        reduced_motion='no-preference',
        forced_colors='none',
        accept_downloads=False,
        screen={'width': 1920, 'height': 1080},
    )
    
    # 添加更复杂的反检测脚本
    await context.add_init_script("""
        // 删除webdriver属性
        delete Object.getPrototypeOf(navigator).webdriver;
        
        // 覆盖plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [{
                0: { type: "application/x-google-chrome-pdf" },
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            }]
        });
        
        // 覆盖languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // 覆盖platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        
        // 覆盖hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // 覆盖deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // 覆盖maxTouchPoints
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 0
        });
        
        // 添加window.chrome
        window.chrome = {
            app: {
                isInstalled: false,
                InstallState: {
                    DISABLED: 'disabled',
                    INSTALLED: 'installed',
                    NOT_INSTALLED: 'not_installed'
                },
                RunningState: {
                    CANNOT_RUN: 'cannot_run',
                    READY_TO_RUN: 'ready_to_run',
                    RUNNING: 'running'
                }
            },
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            webstore: {},
            tts: {},
            ttsEngine: {},
            accessibilityFeatures: {},
            alarms: {},
            bookmarks: {},
            browserAction: {},
            browsingData: {},
            certificates: {},
            contentSettings: {},
            contextMenus: {},
            cookies: {},
            debugger: {},
            declarativeContent: {},
            desktopCapture: {},
            devtools: {},
            downloads: {},
            enterprise: {},
            extension: {},
            fontSettings: {},
            gcm: {},
            history: {},
            i18n: {},
            identity: {},
            idle: {},
            input: {},
            instanceID: {},
            management: {},
            notifications: {},
            omnibox: {},
            pageAction: {},
            pageCapture: {},
            permissions: {},
            platformKeys: {},
            power: {},
            printerProvider: {},
            privacy: {},
            processes: {},
            proxy: {},
            sessions: {},
            storage: {},
            system: {},
            tabCapture: {},
            tabs: {},
            topSites: {},
            types: {},
            vpnProvider: {},
            wallpapers: {},
            webNavigation: {},
            webRequest: {},
            windows: {}
        };
        
        // 覆盖Notification.permission
        Object.defineProperty(Notification, 'permission', {
            get: () => 'default'
        });
        
        // 修改navigator属性
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
        Object.defineProperty(navigator, 'vendorSub', { get: () => '' });
        Object.defineProperty(navigator, 'productSub', { get: () => '20030107' });
        Object.defineProperty(navigator, 'product', { get: () => 'Gecko' });
        
        // 添加屏幕属性
        Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
        Object.defineProperty(screen, 'availHeight', { get: () => 1080 });
        Object.defineProperty(screen, 'width', { get: () => 1920 });
        Object.defineProperty(screen, 'height', { get: () => 1080 });
        Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
        Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
        
        // 修改WebGL指纹
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            if (parameter === 37446) {
                return 'NVIDIA GeForce GTX 1080/PCIe/SSE2';
            }
            return getParameter(parameter);
        };
        
        // 修改canvas指纹
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            const context = this.getContext('2d');
            context.fillRect(0, 0, 10, 10);
            return toDataURL.call(this, type);
        };
    """)
    
    page = await context.new_page()
    
    # 设置超时更长
    page.set_default_timeout(120000)  # 120秒
    page.set_default_navigation_timeout(120000)
    
    return playwright, browser, context, page

async def bypass_cloudflare(page, url):
    """尝试绕过Cloudflare验证"""
    print("🛡️ 尝试绕过Cloudflare...")
    
    # 方法1：使用不同的等待策略
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        print("✅ 使用domcontentloaded加载成功")
        return True
    except:
        pass
    
    # 方法2：使用更简单的等待策略
    try:
        await page.goto(url, wait_until='load', timeout=30000)
        print("✅ 使用load加载成功")
        return True
    except:
        pass
    
    # 方法3：使用networkidle但有更长时间
    try:
        await page.goto(url, wait_until='networkidle', timeout=60000)
        print("✅ 使用networkidle加载成功")
        return True
    except Exception as e:
        print(f"❌ Cloudflare绕过失败: {e}")
        return False

async def login_with_manual_bypass(page, username, password, acc_idx):
    """尝试多种登录策略"""
    try:
        print(f"\n🔐 尝试登录账户 {acc_idx}...")
        
        # 尝试访问登录页
        url = "https://dash.domain.digitalplat.org/auth/login"
        
        # 尝试绕过Cloudflare
        if not await bypass_cloudflare(page, url):
            print("❌ Cloudflare验证无法绕过")
            return False
        
        # 等待更长的时间让验证完成
        await page.wait_for_timeout(15000)  # 15秒
        
        # 检查当前页面内容
        content = await page.content()
        
        # 检查是否还在Cloudflare验证页
        if "verifying" in content.lower() or "cloudflare" in content.lower():
            print("⚠️ 仍在Cloudflare验证页，等待更长时间...")
            await page.wait_for_timeout(20000)  # 再等20秒
        
        # 尝试查找登录表单
        try:
            # 等待页面可能的重定向
            await page.wait_for_timeout(5000)
            
            # 检查当前URL
            current_url = page.url
            print(f"📄 当前URL: {current_url}")
            
            # 尝试多种选择器查找邮箱输入框
            email_selectors = [
                '#email',
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="邮箱" i]',
                'input#emailAddress',
                'input.email',
            ]
            
            email_found = False
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    email_found = True
                    print(f"✅ 找到邮箱输入框: {selector}")
                    break
                except:
                    continue
            
            if not email_found:
                print("❌ 未找到邮箱输入框")
                return False
            
            # 截图当前状态
            await page.screenshot(path=f"debug_acc{acc_idx}_form.png", full_page=True)
            
            # 输入邮箱
            await page.fill(selector, username)
            await page.wait_for_timeout(1000)
            
            # 查找并点击Next按钮
            next_found = False
            next_selectors = [
                'button:has-text("Next")',
                'button:has-text("下一步")',
                'input[type="submit"]',
                'button[type="submit"]',
                'button:has-text("Continue")',
            ]
            
            for next_selector in next_selectors:
                try:
                    await page.wait_for_selector(next_selector, timeout=5000)
                    await page.click(next_selector)
                    next_found = True
                    print(f"✅ 点击Next按钮: {next_selector}")
                    break
                except:
                    continue
            
            if not next_found:
                # 尝试按回车
                await page.keyboard.press('Enter')
                print("⚠️ 尝试按回车键")
            
            # 等待密码框出现
            await page.wait_for_timeout(5000)
            
            # 查找密码输入框
            pwd_selectors = [
                '#password',
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="密码" i]',
            ]
            
            pwd_found = False
            for pwd_selector in pwd_selectors:
                try:
                    await page.wait_for_selector(pwd_selector, timeout=10000)
                    pwd_found = True
                    print(f"✅ 找到密码输入框: {pwd_selector}")
                    break
                except:
                    continue
            
            if not pwd_found:
                print("❌ 未找到密码输入框")
                return False
            
            # 输入密码
            await page.fill(pwd_selector, password)
            await page.wait_for_timeout(1000)
            
            # 查找登录按钮
            login_found = False
            login_selectors = [
                'button:has-text("Login")',
                'button:has-text("登录")',
                'input[value*="Login" i]',
                'input[value*="登录" i]',
                'button[type="submit"]:not(:has-text("Next"))',
            ]
            
            for login_selector in login_selectors:
                try:
                    await page.wait_for_selector(login_selector, timeout=5000)
                    await page.click(login_selector)
                    login_found = True
                    print(f"✅ 点击登录按钮: {login_selector}")
                    break
                except:
                    continue
            
            if not login_found:
                # 尝试在密码框按回车
                await page.keyboard.press('Enter')
                print("⚠️ 在密码框按回车登录")
            
            # 等待登录完成
            await page.wait_for_timeout(15000)
            
            # 检查是否登录成功
            current_url = page.url.lower()
            if "login" not in current_url and "auth" not in current_url:
                print("✅ 登录成功！")
                await page.screenshot(path=f"debug_acc{acc_idx}_success.png", full_page=True)
                return True
            else:
                print("❌ 可能登录失败")
                await page.screenshot(path=f"debug_acc{acc_idx}_failed.png", full_page=True)
                return False
                
        except Exception as e:
            print(f"❌ 登录过程异常: {str(e)[:200]}")
            await page.screenshot(path=f"debug_acc{acc_idx}_error.png", full_page=True)
            return False
            
    except Exception as e:
        print(f"❌ 整体登录异常: {str(e)[:200]}")
        return False

def try_api_login(username, password):
    """尝试使用API登录（如果有的话）"""
    print("🔧 尝试API登录方式...")
    
    # 这里需要根据DPDNS的实际API文档来编写
    # 以下仅为示例代码
    
    # 可能的API端点
    api_endpoints = [
        "https://dash.domain.digitalplat.org/api/auth/login",
        "https://dash.domain.digitalplat.org/api/v1/login",
        "https://api.domain.digitalplat.org/auth",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.post(
                endpoint,
                json={
                    "email": username,
                    "password": password,
                    "remember": True
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ API登录成功: {endpoint}")
                return response.json()
        except:
            continue
    
    print("❌ API登录方式不可用")
    return None

async def renew_domain_simple(page, domain):
    """简化续期流程"""
    try:
        print(f"\n🌐 处理域名: {domain}")
        
        # 直接访问域名管理页
        url = f"https://dash.domain.digitalplat.org/panel/manager/{domain}"
        
        # 使用简单加载策略
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        except:
            await page.goto(url, wait_until='load', timeout=30000)
        
        await page.wait_for_timeout(5000)
        
        # 查找Renew按钮
        try:
            # 先尝试点击Renew标签
            await page.click('button.tab-btn:has-text("Renew")', timeout=5000)
            await page.wait_for_timeout(2000)
        except:
            pass
        
        # 尝试点击Renew按钮
        try:
            await page.click('button:has-text("Renew"):not(.tab-btn)', timeout=10000)
            await page.wait_for_timeout(3000)
            
            # 尝试点击免费续期按钮
            await page.click('button:has-text("Request free renewal")', timeout=10000)
            await page.wait_for_timeout(3000)
            
            print(f"✅ {domain} 续期请求已发送")
            return True
        except:
            print(f"ℹ️ {domain} 可能暂不支持续期")
            return False
            
    except Exception as e:
        print(f"❌ {domain} 处理失败: {str(e)[:100]}")
        return False

async def main_async():
    """主函数"""
    print("=" * 60)
    print("DPDNS 域名自动续期脚本 (高级版)")
    print("=" * 60)
    
    # 首先尝试API方式
    print("\n🔍 首先尝试API方式...")
    
    idx = 1
    while True:
        user = os.environ.get(f'ACCOUNT_{idx}_USERNAME')
        pwd = os.environ.get(f'ACCOUNT_{idx}_PASSWORD')
        doms = os.environ.get(f'ACCOUNT_{idx}_DOMAINS', '')
        
        if not user or not pwd:
            break
        
        print(f"\n{'='*50}")
        print(f"账户 {idx}: {user}")
        print(f"{'='*50}")
        
        # 尝试API登录
        api_result = try_api_login(user, pwd)
        
        if api_result:
            print("🎉 API登录成功，续期逻辑需根据API文档实现")
            # 这里需要根据API文档实现续期逻辑
        else:
            print("🔄 API不可用，尝试浏览器方式...")
            
            playwright = browser = context = page = None
            try:
                # 使用增强的浏览器设置
                playwright, browser, context, page = await setup_stealth_browser()
                
                # 尝试登录
                if await login_with_manual_bypass(page, user, pwd, idx):
                    print("🔓 登录成功，开始检查域名...")
                    domains = [d.strip() for d in doms.split(',') if d.strip()]
                    for domain in domains:
                        await renew_domain_simple(page, domain)
                        await asyncio.sleep(3)
                else:
                    print("⏭️ 登录失败，跳过此账户")
                    
            except Exception as e:
                print(f"❌ 账户 {idx} 处理异常: {e}")
                
            finally:
                # 清理资源
                try:
                    if page:
                        await page.close()
                    if context:
                        await context.close()
                    if browser:
                        await browser.close()
                    if playwright:
                        await playwright.stop()
                except:
                    pass
        
        idx += 1
        await asyncio.sleep(5)
    
    print(f"\n📊 共处理了 {idx-1} 个账户")
    print("\n✨ 脚本执行完成！")

def main():
    """同步入口"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()