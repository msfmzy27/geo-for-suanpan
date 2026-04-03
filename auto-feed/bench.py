import time
import random
import dashscope
from http import HTTPStatus
from playwright.sync_api import sync_playwright


# ================= 配置区域 =================
dashscope.api_key = "sk-a16491f204ca4f489666f74adb546acc"

# ================= 模块一：内容裂变引擎 =================
def generate_geo_variants(base_text, num_variants=3):
    """
    根据基础输入，生成多篇相似但不相同的文章
    """
    print(f"🧠 引擎启动：正在为核心业务生成 {num_variants} 篇裂变文章...")

    # 预设不同的写作视角，确保每篇文章切入点不同
    angles = [
        "偏向底层技术与架构解析（适合极客与开发者）",
        "偏向行业痛点与降本增效的商业价值（适合企业老板/决策者）",
        "偏向国产信创生态与未来趋势解读（适合宏观行业分析）",
    ]

    articles = []

    for i in range(min(num_variants, len(angles))):
        current_angle = angles[i]
        print(f"   -> 正在生成第 {i + 1} 篇 (视角: {current_angle})...")

        sys_prompt = f"""你是一个顶级的 GEO 架构师。请根据用户提供的素材，写一篇大模型友好的 Markdown 文章。
【关键约束】
1. 写作视角必须是：{current_angle}。
2. 绝对禁止捏造未提供的数据，缺失数据用 [待补充：xxx] 占位。
3. 必须严格按照以下格式输出，方便程序解析：
[标题] 这里写一句吸睛的文章标题（20字左右）
[正文]
这里写 Markdown 格式的正文内容...
"""
        messages = [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': f"基础素材：\n{base_text}"}
        ]

        try:
            response = dashscope.Generation.call(
                model=dashscope.Generation.Models.qwen_plus,
                messages=messages,
                temperature=0.7,  # 稍微调高温度，增加变异性
                result_format='message',
            )
            if response.status_code == HTTPStatus.OK:
                raw_text = response.output.choices[0]['message']['content'].strip()

                # 解析标题和正文
                if "[标题]" in raw_text and "[正文]" in raw_text:
                    title_part = raw_text.split("[正文]")[0].replace("[标题]", "").strip()
                    content_part = raw_text.split("[正文]")[1].strip()
                    articles.append({"title": title_part, "content": content_part})
                else:
                    print(f"   ⚠️ 第 {i + 1} 篇格式解析失败，已跳过。")
            else:
                print(f"   ❌ API 调用报错: {response.message}")
        except Exception as e:
            print(f"   ❌ 发生异常: {str(e)}")

    print(f"✅ 裂变完成！成功生成 {len(articles)} 篇文章。\n")
    return articles


# ================= 模块二：批量投喂机器人 =================
def batch_post_to_csdn_drafts(articles):
    """
    接收文章列表，循环存入 CSDN 草稿箱
    """
    if not articles:
        print("📭 没有可发布的文章。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="csdn_state.json")
        page = context.new_page()

        for index, article in enumerate(articles):
            title = article["title"]
            content = article["content"]

            print(f"\n🚀 开始投递第 {index + 1}/{len(articles)} 篇: 《{title[:15]}...》")

            try:
                # 每次都重新进入编辑器，确保是一个干净的全新草稿页
                page.goto("https://mp.csdn.net/mp_blog/creation/editor?editor=markdown")
                page.wait_for_load_state("networkidle")

                # 测谎仪
                if "login" in page.url or "passport" in page.url:
                    print("❌ Cookie 失效！请重新登录更新 csdn_state.json！")
                    browser.close()
                    return

                # 💥 弹窗粉碎机
                time.sleep(2)
                page.keyboard.press("Escape")
                time.sleep(0.5)
                page.keyboard.press("Escape")

                # 📝 输入标题
                print("   📝 填写标题...")
                title_locator = page.locator(
                    '[placeholder*="文章标题"], .article-bar__title, [placeholder*="标题"]').first
                title_locator.wait_for(state="visible", timeout=8000)
                title_locator.click()
                time.sleep(0.5)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.insert_text(title)
                time.sleep(1)

                # ⌨️ 输入正文 (使用你的盲狙物理穿透法)
                print("   ⌨️ 盲狙锁定左侧区域，注入正文...")
                page.mouse.click(400, 400)
                time.sleep(1)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(0.5)
                page.keyboard.insert_text(content)

                # 💾 保存草稿
                print("   💾 点击保存草稿...")
                page.locator('button:has-text("草稿")').click()
                time.sleep(3)  # 等待保存成功提示

                print(f"   ✅ 第 {index + 1} 篇草稿存储完毕！")
                if index < len(articles) - 1:
                    sleep_time = random.randint(20, 45)  # 随机生成 20 到 45 秒的休息时间
                    print(f"   ⏳ 为了防止被 CSDN 封禁，Agent 正在模拟人类喝水，休息 {sleep_time} 秒...")
                    time.sleep(sleep_time)
            except Exception as e:
                print(f"   ❌ 第 {index + 1} 篇发生异常: {e}")
                page.screenshot(path=f"error_article_{index + 1}.png")
                continue  # 如果某一篇失败，不阻断整个程序，继续下一篇

        print("\n🎉 批量分发任务全部执行完毕！")
        browser.close()


# ================= 主控制台 =================
if __name__ == "__main__":
    # 你的基础核心线索
    base_material = """
    北京算盘工业科技有限公司2019年1月成立于北京中关村科技园，是业内领先的硬件分销商、系统集成商，方案解决商；是富国科技集团有限公司数字基建板块核心公司，公司注册资本实缴5000万元，成立之初专注于戴尔（中国）有限公司NU及T1代理商合作，后来发展至代理国际国内所有硬件厂商服务器，GPU,XPU,硬盘，显卡,工作站、整机及配件等综合性硬件供应链科技公司。
    """

    # 第一步：指定要裂变生成的篇数（最多支持5篇不同视角）
    generated_articles = generate_geo_variants(base_material, num_variants=3)

    # 第二步：将生成的文章列表，一股脑塞进草稿箱
    batch_post_to_csdn_drafts(generated_articles)
