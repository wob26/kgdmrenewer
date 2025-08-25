import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """配置并返回一个无头模式的 Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
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
        print(f"[账户 {account_num}] 正在打开登录页面...")
        driver.get("https://register.us.kg/auth/login")
        wait = WebDriverWait(driver, 20)
        
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # 等待登录成功后的页面元素，例如“Dashboard”链接
        wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Dashboard")))
        print(f"[账户 {account_num}] 登录成功。")

        # 2. 导航到域名列表页面
        driver.get("https://register.us.kg/panel/domains")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table"))) # 等待域名表格加载

        # 3. 循环续订每个域名
        domain_list = [d.strip() for d in domains.split(',')]
        for domain in domain_list:
            print(f"  -> 正在处理域名: {domain}...")
            try:
                # 找到包含特定域名的那一行，然后在那一行里找到续期链接
                renew_link_xpath = f"//tr[contains(., '{domain}')]//a[contains(@href, '/renew/')]"
                renew_link = wait.until(EC.element_to_be_clickable((By.XPATH, renew_link_xpath)))
                
                print(f"     找到续期链接，正在点击...")
                renew_link.click()
                
                # 在新页面点击最终的确认续期按钮
                confirm_button_xpath = "//button[@type='submit' and contains(text(), 'Renew')]"
                confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
                print(f"     点击确认按钮...")
                confirm_button.click()
                
                # 检查成功提示
                success_message_xpath = "//*[contains(text(), 'successfully renewed') or contains(text(), 'Domain renewed')]"
                wait.until(EC.presence_of_element_located((By.XPATH, success_message_xpath)))
                print(f"     ✅ 域名 {domain} 续期成功！")

                # 返回域名列表页面以继续处理下一个域名
                driver.get("https://register.us.kg/panel/domains")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            except (TimeoutException, NoSuchElementException) as e:
                print(f"     ❌ 域名 {domain} 续期失败或无需续期。可能原因：续期按钮不存在（未到时间或已续期）。错误: {e}")
                # 出错后也要返回域名列表，以防万一
                driver.get("https://register.us.kg/panel/domains")
                continue # 继续下一个域名

    except Exception as e:
        print(f"处理账户 {username} 时发生严重错误: {e}")
        driver.save_screenshot(f"error_account_{account_num}.png")
    finally:
        driver.quit()
        print(f"[账户 {account_num}] 处理完毕，浏览器已关闭。")


if __name__ == "__main__":
    account_index = 1
    while True:
        # 动态检查是否存在 ACCOUNT_1_USERNAME, ACCOUNT_2_USERNAME 等环境变量
        username = os.environ.get(f'ACCOUNT_{account_index}_USERNAME')
        password = os.environ.get(f'ACCOUNT_{account_index}_PASSWORD')
        domains = os.environ.get(f'ACCOUNT_{account_index}_DOMAINS')

        if username and password:
            renew_account_domains(account_index, username, password, domains)
            account_index += 1
        else:
            # 如果找不到下一个账户的配置，说明所有账户都已处理完毕
            if account_index == 1:
                print("错误：未找到任何账户配置。请检查 GitHub Secrets 是否已正确设置 (例如 ACCOUNT_1_USERNAME)。")
            break
    print(f"\n所有 {account_index - 1} 个账户均已处理完毕。")
