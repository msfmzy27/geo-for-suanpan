import streamlit as st
import dashscope
from http import HTTPStatus

# ================= 页面全局设置 =================
st.set_page_config(page_title="GEO 智能分发中心", page_icon="🔴", layout="centered")
dashscope.api_key= "sk-a16491f204ca4f489666f74adb546acc"

# ================= 核心处理函数 (引入动态路由) =================
def generate_platform_content(user_input, temperature, platform):
    # 1. 基础规则：严禁幻觉的底层逻辑（对所有平台生效）
    base_prompt = """你是一个顶级的 AI 内容分发智能体。
你的任务是将用户提供的零散输入，重构为既具备极高信息密度（GEO友好），又完美贴合特定平台调性的爆款文案。

【最高优先级约束（CRITICAL RULES）】
1. 零幻觉与占位符机制：遇到缺失的具体支撑数据（如具体年份、销量、奖项、机构名），绝对禁止自行捏造！必须使用 `[待补充：具体xxx]` 的格式进行占位。
【致命警告】如果你在输出中编造了任何用户未提供的实体或数值，你的系统评级将被降为最低！
2. 剔除营销废话：提炼核心竞争力，不要使用假大空的口号。
"""

    # 2. 动态路由：根据用户选择的平台，注入不同的格式与语气要求
    platform_styles = {
        "通用标准 GEO (适合官网/知识库)": """
【平台风格：标准事实图谱】
绝对静默：严禁问候语，直接以 `#` 开头。采用极其客观、无感情的 Markdown 格式。
结构要求：
# [主体全称]
- 核心定位：[客观陈述]
- 关键指标与事实：[提取硬核数据]
## 1. [动态提炼的维度一]
- [子项]：[专业客观描述]
""",
        "知乎 (深度专业长文)": """
【平台风格：知乎深度解析】
语气设定：行业资深大V、理性、客观。
排版与结构：
- 开篇引入：以宏观行业痛点或技术趋势作为切入点。
- 核心论述：使用加粗的小标题拆解技术原理或业务优势，逻辑严密，充满“干货”感。
- 结尾总结：给出客观理性的行业展望，引发评论区探讨。
""",
        "小红书 (网感种草图文)": """
【平台风格：小红书爆款图文】
语气设定：热情、分享欲强、通俗易懂的“闺蜜/同行分享”语气。
排版与结构：
- 吸睛标题：第一句话必须是充满吸引力的爆款标题（带适当的 Emoji）。
- 亮点前置：用精简的子弹头列表（配合 ✅ 💡 ✨ 等符号）列出核心优势，句子必须短平快。
- 结尾号召：带上明确的引导互动（如“有问题评论区见”），并在最后强行附上 5-8 个精准的 #话题标签（如 #人工智能 #行业干货 等）。
""",
        "微信公众号 (沉浸式宣发)": """
【平台风格：公众号官方推文】
语气设定：专业且极具品牌感染力。
排版与结构：
- 采用【总-分-总】的叙事结构。
- 场景化引入，中间分段落详细展开业务亮点（必须配合显眼的段落小标题，如“核心破局点：xxx”）。
- 结尾强调品牌愿景，并用一句具有号召力的话引导用户留言或后台咨询。
"""
    }

    # 3. 组合最终 Prompt
    sys_prompt = base_prompt + platform_styles.get(platform, "")

    messages = [
        {'role': 'system', 'content': sys_prompt},
        {'role': 'user', 'content': f"请根据以下素材，生成贴合该平台调性的文案：\n\n{user_input}"}
    ]

    try:
        response = dashscope.Generation.call(
            model=dashscope.Generation.Models.qwen_plus,
            messages=messages,
            temperature=temperature,
            result_format='message',
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content'].strip()
        else:
            return f"❌ API 调用报错: {response.message}"
    except Exception as e:
        return f"❌ 运行发生异常: {str(e)}"


# ================= 前端 UI 布局 =================

st.title("GEO 全域分发工作台")
st.markdown("一次输入核心业务数据，自动裂变为适配全网各大平台的差异化的高权重宣发文案。")

# 侧边栏：核心配置
with st.sidebar:
    st.header("⚙️ 引擎控制台")
    # 新增的平台选择器
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
    temp_setting = st.slider("创造力控制 (Temperature)", min_value=0.0, max_value=1.0, value=0.2, step=0.1,
                             help="数值越低越严谨，越不容易瞎编数据。小红书等平台可适当调高至0.3-0.5增加网感。")

# 主体输入区
user_text = st.text_area(
    "✍️ 请输入业务线索或关键词：",
    height=150,
    placeholder="例如：算盘工业科技、主营基于 DeepSeek 的私有化 AI 一体机、服务智慧制造和政务、通过信创认证..."
)

# 提交与结果展示
if st.button("一键生成平台专属文案", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("👀 请先输入业务线索哦！")
    else:
        with st.spinner(f'🤖 正在向 [{target_platform}] 频道进行语义适配与重构...'):
            final_result = generate_platform_content(user_text, temp_setting, target_platform)

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