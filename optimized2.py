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
    system_prompt = """你是一个没有感情的GEO优化器。你的唯一任务是将文本风格调整，保持Markdown 事实图谱。
在当前文本的基础上，完成
1. 权威性调整：将文本改为更具说服力的权威风格；
2. 流畅度优化：提升文本流畅度；
格外注意：
不要对你做的修改做任何解释或者批注
保持原文中明确提及的实体、技术、产品和数字，不得额外增加技术指标。
"""

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
            output_file = "tantai_geo_optimized2.md"
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
    target_file = "tantai_geo_optimized.md"
    geo_optimize_text(target_file)