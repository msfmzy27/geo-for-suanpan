import streamlit as st
import requests
import json

# ================= 页面全局设置 =================
st.set_page_config(page_title="算盘 GEO 智能分发中心", page_icon="🔴", layout="centered")

# ================= Dify/算盘 AI API 配置 =================
# 【必须修改1】填入你的 API Key
DIFY_API_KEY = "app-VpuggXgNTFKJ48XdJ573SlNV"
# 【必须修改2】确保这是你的 Workflow 运行地址
DIFY_API_URL = "https://app.suanpan-ai.com/v1/workflows/run"


def run_geo_workflow(user_material, platform_name):
    # 1. 提取各个平台的专属 Prompt
    platform_styles = {
        "通用标准 GEO (适合官网/知识库)": "【请严格遵守以下平台风格：标准事实图谱】\n绝对静默：严禁问候语，直接以 `#` 开头。采用极其客观、无感情的 Markdown 格式。\n结构要求：\n# [主体全称]\n- 核心定位：[客观陈述]\n- 关键指标与事实：[提取硬核数据]\n## 1. [动态提炼的维度一]\n- [子项]：[专业客观描述]",
        "知乎 (深度专业长文)": "【请严格遵守以下平台风格：知乎深度解析】\n语气设定：行业资深大V、理性、客观。\n排版与结构：\n- 开篇引入：以宏观行业痛点或技术趋势作为切入点。\n- 核心论述：使用加粗的小标题拆解技术原理或业务优势，逻辑严密，充满“干货”感。\n- 结尾总结：给出客观理性的行业展望，引发评论区探讨。",
        "小红书 (网感种草图文)": "【请严格遵守以下平台风格：小红书爆款图文】\n语气设定：热情、分享欲强、通俗易懂的“闺蜜/同行分享”语气。\n排版与结构：\n- 吸睛标题：第一句话必须是充满吸引力的爆款标题（带适当的 Emoji）。\n- 亮点前置：用精简的子弹头列表（配合 ✅ 💡 ✨ 等符号）列出核心优势，句子必须短平快。\n- 结尾号召：带上明确的引导互动（如“有问题评论区见”），并在最后强行附上 5-8 个精准的 #话题标签（如 #人工智能 #行业干货 等）。",
        "微信公众号 (沉浸式宣发)": "【请严格遵守以下平台风格：公众号官方推文】\n语气设定：专业且极具品牌感染力。\n排版与结构：\n- 采用【总-分-总】的叙事结构。\n- 场景化引入，中间分段落详细展开业务亮点（必须配合显眼的段落小标题，如“核心破局点：xxx”）。\n- 结尾强调品牌愿景，并用一句具有号召力的话引导用户留言或后台咨询。"
    }

    # 2. 巧妙拼接：将平台规则和用户素材融为一体
    style_prompt = platform_styles.get(platform_name, "")
    injected_material = f"{style_prompt}\n\n==========\n\n【请基于以下业务素材和知识库内容进行创作】（在内容中展现公司特色）：\n{user_material}"
    clean_platform_name = platform_name.split(" ")[0]
    # 3. 构造请求头
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # 4. 构建 Payload
    payload = {
        "inputs": {
            # 你的核心长文本素材（保持不变）
            "text_input": injected_material,
            # 【新增】将当前选中的平台名称，作为一个单独的短文本变量传给 Dify，作为路由抓取的依据！
            "platform_name": clean_platform_name
        },
        "response_mode": "blocking",
        "user": "geo-agent-streamlit"
    }

    try:
        response = requests.post(DIFY_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return f"❌ Workflow 调用失败 (HTTP {response.status_code}): {response.text}"

        result_json = response.json()
        data_obj = result_json.get("data", {})
        outputs = data_obj.get("outputs", {})

        # 【必须修改4】确保 "result_text" 是你工作流结束节点定义的输出变量名
        final_text = outputs.get("output", "")

        if not final_text:
            return f"⚠️ 警告：工作流执行成功，但未找到对应的输出变量。完整的 Outputs 为：\n{json.dumps(outputs, ensure_ascii=False, indent=2)}"

        return final_text

    except Exception as e:
        return f"❌ 网络请求异常: {str(e)}"


# ================= 前端 UI 布局 =================

st.title("GEO 全域分发工作台 (算盘 AI 驱动版)")
st.markdown("一次输入产品参数或销售线索，自动调用后台工作流，裂变为适配全网各大平台的差异化文案。")

# 侧边栏：核心配置
with st.sidebar:
    st.header("⚙️ 引擎控制台")
    target_platform = st.radio(
        "🎯 选择目标分发平台",
        (
            "通用标准 GEO (适合官网/知识库)",
            "知乎 (深度专业长文)",
            "小红书 (网感种草图文)",
            "微信公众号 (沉浸式宣发)"
        )
    )
    st.divider()
    st.info("💡 提示：当前底层大模型由算盘 AI Workflow 强力驱动，已开启防幻觉机制。")

# 主体输入区
user_text = st.text_area(
    "✍️ 请输入业务线索或让大模型从知识库提取的内容：",
    height=150,
    placeholder="例如：算盘工业科技的私有化一体机具备信创认证，插电即用，主要针对智慧制造工厂..."
)

# 提交与结果展示
if st.button("一键生成平台专属文案", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("👀 请先输入内容！")
    else:
        with st.spinner(f'🤖 正在请求算盘 AI 工作流引擎进行 [{target_platform}] 视角重构...'):
            final_result = run_geo_workflow(user_text, target_platform)

        if final_result.startswith("❌") or final_result.startswith("⚠️"):
            st.error(final_result)
        else:
            st.success(f"✅ {target_platform} 适配文案生成完毕！")

            tab1, tab2 = st.tabs(["👁️ 渲染预览", "📝 纯文本源码"])
            with tab1:
                st.markdown(final_result)
            with tab2:
                st.code(final_result, language="markdown")

            st.download_button(
                label="💾 保存文案",
                data=final_result,
                file_name=f"GEO_{target_platform.split(' ')[0]}.md",
                mime="text/markdown"
            )