import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
# 【新增】导入 Service 和 ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """【已修改】使用 webdriver-manager 配置并返回一个无头模式的 Chrome WebDriver"""
    chrome_options = Options()
    # 使用 --headless=new 是更现代的无头模式标志
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 增加 --disable-gpu 选项，有时在Linux服务器上是必需的
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 【核心修改】使用 webdriver-manager 自动安装并配置与浏览器匹配的驱动
    # 它会检测到我们安装的Chrome 114，并下载正确的驱动程序
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def renew_account_domains(account_num, username, password, domains):
    """登录一个账户并续订其下所有指定的域名"""
    print(f"\n{'='*20}\n[账户 {account_num}: {username}] 开始处理...")
    if not domains:
        print(f"[账户 {account_num}] 未配置任何域名，跳过。")
        return

    driver = setup_driver()
    try:
        # 1. 登录
        login_url = "https://dash.domain.digitalplat.org/auth/login"
        print(f"[账户 {account_num}] 正在打开登录页面: {login_url}...")
        driver.get(login_url)
        wait = WebDriverWait(driver, 20)
        
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Dashboard")))
        print(f"[账户 {account_num}] 登录成功。")

        # 2. 循环续订每个域名
        domain_list = [d.strip() for d in domains.split(',')]
        domains_panel_url = "https://dash.domain.digitalplat.org/panel/domains"

        for domain in domain_list:
            print(f"  -> 正在处理域名: {domain}...")
            try:
                # 3. 导航到域名列表页面
                print(f"     导航至域名列表...")
                driver.get(domains_panel_url)
                
                # 4. 找到并点击特定域名的 "Manage" 链接
                manage_link_xpath = f"//tr[contains(., '{domain}')]//a[contains(@href, 'panel/manage')]"
                manage_link = wait.until(EC.element_to_be_clickable((By.XPATH, manage_link_xpath)))
                print(f"     找到 {domain} 的管理链接，正在点击...")
                manage_link.click()

                # 5. 点击 "Renew" 标签页按钮
                renew_tab_button_xpath = "//button[contains(@class, 'tab-btn') and normalize-space()='Renew']"
                renew_tab_button = wait.until(EC.element_to_be_clickable((By.XPATH, renew_tab_button_xpath)))
                print(f"     找到 'Renew' 标签页按钮，正在点击...")
                renew_tab_button.click()
                
                time.sleep(1)

                # 6. 点击 "Free Renewal" 按钮
                free_renewal_button_xpath = "//button[contains(text(), 'Free Renewal (Available if less than 180 days left)')]"
                free_renewal_button = wait.until(EC.element_to_be_clickable((By.XPATH, free_renewal_button_xpath)))
                print(f"     找到 'Free Renewal' 按钮，正在点击...")
                free_renewal_button.click()

                # 7. 在最终确认页面上，点击提交按钮
                final_confirm_button_xpath = "//button[@type='submit']"
                final_confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, final_confirm_button_xpath)))
                print(f"     找到最终确认按钮，正在点击...")
                final_confirm_button.click()

                # 8. 检查成功提示
                success_message_xpath = "//*[contains(text(), 'Success') or contains(text(), 'successfully') or contains(text(), 'renewed')]"
                wait.until(EC.presence_of_element_located((By.XPATH, success_message_xpath)))
                print(f"     ✅ 域名 {domain} 续期成功！")

            except (TimeoutException, NoSuchElementException):
                print(f"     ❌ 域名 {domain} 续期失败或无需续期。可能原因：未到续期时间或页面结构已改变。")
                driver.save_screenshot(f"error_{domain}.png")
                continue

    except Exception as e:
        print(f"处理账户 {username} 时发生严重错误: {e}")
        driver.save_screenshot(f"error_account_{account_num}.png")
    finally:
        driver.quit()
        print(f"[账户 {account_num}] 处理完毕，浏览器已关闭。")


if __name__ == "__main__":
    account_index = 1
    while True:
        username = os.environ.get(f'ACCOUNT_{account_index}_USERNAME')
        password = os.environ.get(f'ACCOUNT_{account_index}_PASSWORD')
        domains = os.environ.get(f'ACCOUNT_{account_index}_DOMAINS')

        if username and password:
            renew_account_domains(account_index, username, password, domains)
            account_index += 1
        else:
            if account_index == 1:
                print("错误：未找到任何账户配置。请检查 GitHub Secrets 是否已正确设置 (例如 ACCOUNT_1_USERNAME)。")
            break
    print(f"\n所有 {account_index - 1} 个账户均已处理完毕。")
