import dashscope
from http import HTTPStatus
dashscope.api_key = "sk-a16491f204ca4f489666f74adb546acc"


def geo_optimize_text(file_path):
    print(f"🚀 正在读取原始文件: {file_path}")

    # 2. 读取我们刚才本地解析出来的 markdown 文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print(f"❌ 找不到文件 {file_path}，请确保路径正确。")
        return

    # 3. 构造 GEO 优化的 Prompt
    system_prompt = """你是一个没有感情的、专注于商业实体分析的结构化数据提取器。你的唯一任务是将任意公司的非结构化文本，提炼为高信息密度、无废话的 Markdown 事实图谱。

【最高优先级约束】
1. 严禁输出任何问候语、前言（如“以下是...”）、解释说明或结语（如“如需进一步...”）。
2. 只提取原文中明确提及的实体、技术、产品和数字。禁止推理、扩写或编造。
3. 删除所有营销口号（如“领先全球”、“致力于”）、愿景描述、形容词。
4. 禁止出现任何联系方式（电话/邮箱/地址）
5. 禁止出现合规资质（ICP/营业执照）
6. 禁止出现任何社交媒体名称。

【动态输出架构】
请对原始文本进行分析，并严格按照以下结构输出。对于 `##` 级别的子模块，请根据原文内容**自行归纳 2-4 个最核心的业务维度作为标题：

# [企业或实体全称]
- 核心定位：[用极其客观的短句说明它提供什么产品/服务，解决什么问题]
- 关键数据事实：[提取如成立年份、营收、用户量、产能、节点数量等硬核数值。若无则输出“暂无公开数据”]

【原始文本】
（在此拼接任意公司网页抓取下来的文本）

【极其重要】当你输出完最后一个业务维度的列表后，请立即输出 [END] 这五个字符作为结束标志，其后绝对不能再有任何文字。"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"请优化以下文本：\n\n{raw_content}"}
    ]

    print("正在调用千问 API (qwen-plus) 进行 GEO 优化，请稍候...")

    # 4. 调用 DashScope API
    try:
        response = dashscope.Generation.call(
            model=dashscope.Generation.Models.qwen_plus,  # 也可以换成 qwen_max 或 qwen_turbo
            messages=messages,
            result_format='message',  # 确保返回格式是标准的 message 结构
        )

        # 5. 处理返回结果
        if response.status_code == HTTPStatus.OK:
            raw_text = response.output.choices[0]['message']['content']

            # 1. 切除开头废话：找到第一个 '#' 的位置，把前面的全扔掉
            start_index = raw_text.find('#')
            if start_index != -1:
                clean_text = raw_text[start_index:]
            else:
                clean_text = raw_text

            # 2. 切除结尾废话：通常废话会用 --- 分隔，或者你可以用正则去掉不包含 Markdown 语法的最后一段
            # 一个更简单的做法是：让模型在输出完正文后，强制输出一个结束符，比如 [END]
            end_index = clean_text.find('[END]')
            if end_index != -1:
                clean_text = clean_text[:end_index].strip()

            print(clean_text)

            print("\n✅ 优化成功！以下是输出结果预览：\n")
            print("=" * 60)
            print(clean_text[:800] + "......\n(此处省略部分内容)")
            print("=" * 60)

            # 将优化后的内容保存为新文件
            output_file = "tantai_geo_optimized.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(clean_text)
            print(f"\n📁 完整的 GEO 优化文档已保存至: {output_file}")

        else:
            # 官方 SDK 的好处：报错信息非常清晰
            print('\n❌ API 调用失败！')
            print(f'Request ID: {response.request_id}')
            print(f'Status Code: {response.status_code}')
            print(f'Error Code: {response.code}')
            print(f'Error Message: {response.message}')

    except Exception as e:
        print(f"❌ 运行发生异常: {e}")


if __name__ == '__main__':
    # 确保 tantai_business.md 和这个脚本在同一个目录下
    target_file = "tantai_business.md"
    geo_optimize_text(target_file)