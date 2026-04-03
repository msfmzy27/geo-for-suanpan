from playwright.sync_api import sync_playwright


def save_login_state():
    with sync_playwright() as p:
        # headless=False 让我们能看到浏览器界面
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 打开 CSDN 登录页
        page.goto("https://passport.csdn.net/login")

        print("🚨 请在弹出的浏览器中进行扫码或密码登录...")
        print("🚨 登录成功，看到 CSDN 首页后，请回到这里按下【回车键】！")
        input()  # 程序会在这里卡住，等你登录完按回车

        # 把登录状态（Cookie/Token）保存下来
        context.storage_state(path="csdn_state.json")
        print("✅ 登录状态已成功保存到 csdn_state.json！你可以关掉这个终端了。")

        browser.close()


if __name__ == "__main__":
    save_login_state()