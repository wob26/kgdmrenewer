import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- 从环境变量中获取机密信息 ---
USERNAME = os.environ.get('KG_USERNAME')
PASSWORD = os.environ.get('KG_PASSWORD')
DOMAIN_TO_RENEW = os.environ.get('KG_DOMAIN')

if not all([USERNAME, PASSWORD, DOMAIN_TO_RENEW]):
    print("错误：请确保在 GitHub Secrets 中设置了 KG_USERNAME, KG_PASSWORD 和 KG_DOMAIN")
    exit(1)

# --- 脚本主程序 ---
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，在服务器上运行不需要图形界面
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def renew_domain(driver):
    print("开始自动续期脚本...")
    try:
        print("正在打开登录页面...")
        driver.get("https://register.us.kg/auth/login")
        wait = WebDriverWait(driver, 20)
        
        print("输入用户名...")
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        username_field.send_keys(USERNAME)

        print("输入密码...")
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(PASSWORD)
        
        print("点击登录按钮...")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        print("登录成功，等待跳转到域名管理页面...")
        # 注意: 登录后可能会直接跳转到域名列表，也可能需要手动点击
        # 我们直接导航到域名页面以确保流程一致
        domains_url = "https://register.us.kg/panel/domains"
        driver.get(domains_url)
        
        print(f"正在查找域名 {DOMAIN_TO_RENEW} 的续期按钮...")
        renew_button_xpath = f"//tr[contains(., '{DOMAIN_TO_RENEW}')]//a[contains(@href, '/renew/')]"
        renew_button = wait.until(EC.element_to_be_clickable((By.XPATH, renew_button_xpath)))
        
        print("找到续期按钮，正在点击...")
        renew_button.click()

        # 等待确认页面加载（如果需要）并点击确认
        print("等待续期确认页面...")
        # 假设续期确认按钮在一个表单里，并且是提交类型
        confirm_button_xpath = "//button[@type='submit' and contains(text(), 'Renew')]"
        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
        
        print("点击确认续期按钮...")
        confirm_button.click()
        
        print("续期操作已成功触发！等待最终结果页面...")
        # 检查页面上是否有成功提示
        success_message = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'successfully renewed')]")))
        print(f"成功信息: {success_message.text}")
        print("自动续期流程成功完成！")

    except Exception as e:
        print(f"脚本执行过程中发生错误: {e}")
        # 截图以帮助调试
        driver.save_screenshot("error_screenshot.png")
        raise e
    finally:
        driver.quit()
        print("脚本执行完毕，浏览器已关闭。")

if __name__ == "__main__":
    driver = setup_driver()
    renew_domain(driver)
