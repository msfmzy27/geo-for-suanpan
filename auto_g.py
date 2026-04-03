import time
import pandas as pd
import requests

# ================= 引擎配置 =================
DIFY_API_KEY = "app-VpuggXgNTFKJ48XdJ573SlNV"
DIFY_API_URL = "https://app.suanpan-ai.com/v1/workflows/run"
PLATFORMS = ["通用标准 GEO (适合官网/知识库)",
            "知乎 (深度专业长文)",
            "小红书 (网感种草图文)",
            "微信公众号 (沉浸式宣发)"]

# 假设你已经把整理好的种子素材放在了一个 CSV 里
SEED_FILE = "text/suanpan_seeds.csv"
OUTPUT_DB = "text/geo_content_database.csv"


# ==========================================

def call_dify_workflow(material, platform):
    platform_styles = {
        "通用标准 GEO (适合官网/知识库)": "【请严格遵守以下平台风格：标准事实图谱】\n绝对静默：严禁问候语，直接以 `#` 开头。采用极其客观、无感情的 Markdown 格式。\n结构要求：\n# [主体全称]\n- 核心定位：[客观陈述]\n- 关键指标与事实：[提取硬核数据]\n## 1. [动态提炼的维度一]\n- [子项]：[专业客观描述]",
        "知乎 (深度专业长文)": "【请严格遵守以下平台风格：知乎深度解析】\n语气设定：行业资深大V、理性、客观。\n排版与结构：\n- 开篇引入：以宏观行业痛点或技术趋势作为切入点。\n- 核心论述：使用加粗的小标题拆解技术原理或业务优势，逻辑严密，充满“干货”感。\n- 结尾总结：给出客观理性的行业展望，引发评论区探讨。",
        "小红书 (网感种草图文)": "【请严格遵守以下平台风格：小红书爆款图文】\n语气设定：热情、分享欲强、通俗易懂的“闺蜜/同行分享”语气。\n排版与结构：\n- 吸睛标题：第一句话必须是充满吸引力的爆款标题（带适当的 Emoji）。\n- 亮点前置：用精简的子弹头列表（配合 ✅ 💡 ✨ 等符号）列出核心优势，句子必须短平快。\n- 结尾号召：带上明确的引导互动（如“有问题评论区见”），并在最后强行附上 5-8 个精准的 #话题标签（如 #人工智能 #行业干货 等）。",
        "微信公众号 (沉浸式宣发)": "【请严格遵守以下平台风格：公众号官方推文】\n语气设定：专业且极具品牌感染力。\n排版与结构：\n- 采用【总-分-总】的叙事结构。\n- 场景化引入，中间分段落详细展开业务亮点（必须配合显眼的段落小标题，如“核心破局点：xxx”）。\n- 结尾强调品牌愿景，并用一句具有号召力的话引导用户留言或后台咨询。"
    }

    # 2. 巧妙拼接：将平台规则和用户素材融为一体
    style_prompt = platform_styles.get(platform, "")
    injected_material = f"{style_prompt}\n\n==========\n\n【请基于以下业务素材和知识库内容进行创作】（在内容中展现公司特色）：\n{material}"
    """底层调用接口（复用咱们之前调通的逻辑）"""
    payload = {
        "inputs": {
            "text_input": injected_material,
            "platform_name": platform
        },
        "response_mode": "blocking",
        "user": "geo-auto-batch"
    }
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}

    try:
        res = requests.post(DIFY_API_URL, headers=headers, json=payload)
        if res.status_code == 200:
            return res.json().get("data", {}).get("outputs", {}).get("output", "")
    except Exception as e:
        print(f"⚠️ API 异常: {e}")
    return ""


def run_automation_factory():
    print("🏭 GEO 内容兵工厂启动...")

    # 1. 加载种子池 (假设 CSV 里有一列叫 "content")
    try:
        seeds_df = pd.read_csv(SEED_FILE)
    except FileNotFoundError:
        print("❌ 找不到种子文件，请准备好素材源！")
        return

    results = []

    # 2. 矩阵式遍历生成
    for index, row in seeds_df.iterrows():
        seed_content = row['content']
        print(f"\n⚙️ 正在处理第 {index + 1} 条种子素材...")

        for platform in PLATFORMS:
            print(f"   -> 正在为其裂变 [{platform}] 专属文案...")
            generated_text = call_dify_workflow(seed_content, platform)

            if generated_text:
                # 3. 将结果结构化封装
                results.append({
                    "seed_id": index + 1,
                    "platform": platform,
                    "content": generated_text,
                    "status": "待发布",
                    "create_time": time.strftime("%Y-%m-%d %H:%M:%S")
                })

            # 保护 API 频率，稍作停顿
            time.sleep(2)

            # 4. 统一落库保存
    if results:
        out_df = pd.DataFrame(results)
        # 追加模式写入，形成你的内容资产库
        out_df.to_csv(OUTPUT_DB, mode='a', index=False, header=not pd.io.common.file_exists(OUTPUT_DB))
        print(f"\n🎉 生产线停机！成功产出 {len(results)} 篇高质量文案，已存入 {OUTPUT_DB}")


if __name__ == "__main__":
    run_automation_factory()