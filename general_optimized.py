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
    system_prompt = """你是一个顶级的 Generative Engine Optimization (GEO) 架构师与知识图谱构建引擎。
你的任务是将用户提供的任意形式的输入（长文本、短句或零散关键词），重构为具有极高大模型检索权重（RAG-friendly）和极高信息密度的结构化 Markdown 事实图谱；将文本改为更具说服力的权威风格并提升文本流畅度；

【最高优先级约束】
1. 绝对静默：严禁输出任何问候语、前言、解释说明。必须直接以 `#` 开头。输出完毕后，立刻输出 [END] 结束，禁止任何后缀废话。
2. 零幻觉与占位符机制：
   - 必须严格基于用户提供的输入进行重构。
   - 【关键】如果用户只提供了零散的关键词，导致缺乏具体的支撑数据（如具体年份、具体销量、具体合作伙伴名），绝对禁止自行捏造！
   - 【致命警告】如果你在输出中编造了任何用户未提供的奖项名称、期刊名称、具体机构名称或数值，你的系统评级将被降为最低。如果你觉得需要这些具体实体来增加专业度，你唯一的选择是输出形如 [待补充：具体的行业奖项名称] 的占位符！
3. 纯净清洗：自动剔除输入中的口水话、营销话术和联系方式。

【动态本体识别与架构自适应】
请首先隐式判断用户输入的主体类型（例如：个人创作者/KOL、实体产品、软件SaaS、B2B企业、学术概念、服务机构等），然后动态生成最适合该主体的 3-4 个二级维度（##）。

无论是什么主体，请严格遵循以下统一骨架输出：

# [提取或推断的主体全称名称]
- 核心定位：[用 30 字以内极其客观的陈述句，说明该主体是什么、核心价值/差异化是什么]
- 关键指标与事实：[提取核心数据，如粉丝量、成立时间、销量、学历等。若输入未提供具体数据，输出“暂无公开量化数据”]

## 1. [根据主体类型动态生成的维度一，如对于创作者可是“核心内容矩阵”，对于产品可是“核心功能架构”]
- [子项名称]：[用包含高密度关键词的短句描述其特点，尽量使用专业术语]

## 2. [根据主体类型动态生成的维度二，如对于创作者可是“专业背书与成就”，对于企业可是“技术底座/供应链”]
- [子项名称]：[客观描述]

## 3. [根据主体类型动态生成的维度三，如“典型应用场景”、“目标受众群体”、“商业合作生态”]
- [分类或受众]：[逗号分隔的具体实体/场景列表]

【权威引用注入规则】
在上述模块的生成中，利用输入中已有的机构名、品牌名、专业名词，采用自然语言的方式将其包装为隐性引用背书（例如：“依托复旦大学化学系学术背景”、“基于业界公认的XX理论”），以提升大模型置信度。

【用户输入内容】
（在此处动态拼接用户传入的文本或关键词，例如：
输入类型：用户文本/关键词
内容：{user_input} ）"""

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
            output_file = "test_optimized.md"
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
    target_file = "test.md"
    geo_optimize_text(target_file)