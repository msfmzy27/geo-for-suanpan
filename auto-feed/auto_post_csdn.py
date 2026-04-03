from playwright.sync_api import sync_playwright
import time


def auto_post_to_csdn(title, markdown_content):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="csdn_state.json")
        page = context.new_page()

        print("🚀 正在强行进入 CSDN Markdown 创作后台...")
        page.goto("https://mp.csdn.net/mp_blog/creation/editor?editor=markdown")
        page.wait_for_load_state("networkidle")

        # ==================== 💥 弹窗粉碎机 💥 ====================
        print("🔍 正在清理可能的干扰弹窗...")
        time.sleep(2)  # 稍微等两秒，让 AI 助手弹窗飞一会儿

        # 绝招1：连按两次 ESC 键，能关掉 90% 的页面浮窗
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.keyboard.press("Escape")

        # 绝招2：如果 ESC 不管用，尝试精准点击那个关闭按钮
        try:
            close_btn = page.locator('i[class*="close"], span[class*="close"]').filter(has_text="").last
            if close_btn.is_visible():
                close_btn.click()
                print("💥 已物理击碎 AI 助手弹窗！")
        except:
            pass  # 没找到就算了，可能已经被 ESC 关掉了
        # =========================================================

        # ================= 测谎仪：检查是否被踢回登录页 =================
        current_url = page.url
        print(f"📍 当前页面 URL: {current_url}")
        if "login" in current_url or "passport" in current_url:
            print("❌ 完蛋，Cookie 失效或未生效！CSDN 把你踢回登录页了。")
            print("👉 解决办法：删掉 csdn_state.json，重新运行 login_csdn.py 扫码登录一次！")
            browser.close()
            return
        # ==============================================================

        try:
            print("📝 正在输入标题...")
            title_locator = page.locator('[placeholder*="文章标题"], .article-bar__title, [placeholder*="标题"]').first
            title_locator.wait_for(state="visible", timeout=10000)

            title_locator.click()
            time.sleep(0.5)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.insert_text(title)
            time.sleep(1)

            print("⌨️ 正在定位正文编辑器...")
            # 【终极物理穿透法】计算整个编辑器的大框坐标，强制点击它的左半边（输入区）

            page.mouse.click(400, 400)  # 盲点屏幕左侧

            time.sleep(1)  # 给光标0.5秒的闪烁反应时间

            print("🧹 清理默认提示词...")
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.5)

            print("⌨️ 正在狂飙输入 GEO 文案...")
            # 瞬间粘贴大段文本
            page.keyboard.insert_text(markdown_content)

            print("💾 正在保存到草稿箱...")
            page.locator('button:has-text("草稿")').click()

            time.sleep(3)
            print("🎉 自动化流转成功！请去 CSDN 草稿箱查看。")

        except Exception as e:
            print(f"❌ 自动化过程发生异常：{e}")
            page.screenshot(path="error_screenshot_final.png")
            print("📸 已拍下案发现场照片 error_screenshot_final.png")

        finally:
            browser.close()


if __name__ == "__main__":
    test_title = "基于 DeepSeek 的私有化 AI 一体机：算盘工业架构解析"
    test_content = """# 算盘工业科技：AI一体机与信创生态引领者
- **核心定位**：专注 DeepSeek 私有化部署与信创服务器集成的数字基建服务商。

## 1. 核心技术底座
依托英伟达与国产算力芯片，打造高可用软硬协同架构...
"""
    auto_post_to_csdn(test_title, test_content)