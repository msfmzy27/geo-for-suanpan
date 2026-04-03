import re
import pandas as pd
import os

# ================= 配置区 =================
INPUT_TXT = "suanpan_merged_knowledge.txt"  # 刚才聚合的长文本文件
OUTPUT_CSV = "suanpan_seeds.csv"  # 即将生成的结构化种子池


# ==========================================

def create_seed_pool():
    print(f"⚙️ 正在读取原始语料文档: {INPUT_TXT}")

    if not os.path.exists(INPUT_TXT):
        print("❌ 找不到原始文档，请确认文件名是否正确！")
        return

    # 1. 读取完整的超级文档
    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        full_text = f.read()

    # 2. 动用正则表达式“菜刀”
    # \d+ 代表匹配任意数字，这个正则会完美匹配所有形态的分割线
    split_pattern = r'================ \[第 \d+ 篇官方资讯\] ================'

    # 按分割线将长文本切成一个列表
    raw_articles = re.split(split_pattern, full_text)

    seeds = []

    # 3. 清洗切出来的碎片
    for article in raw_articles:
        clean_text = article.strip()
        # 过滤掉切割时可能产生的空字符串
        if len(clean_text) > 10:
            seeds.append(clean_text)

    print(f"🔪 成功切分出 {len(seeds)} 块独立生肉素材！")

    # 4. 结构化落库：转为 DataFrame 并存为 CSV
    # 使用 pd.DataFrame 将其转化为标准的表格格式，列名为 "content"
    df = pd.DataFrame({"content": seeds})

    # 🌟 关键细节：使用 utf-8-sig 编码保存
    # 这样你如果直接用 Windows 的 Excel 双击打开这个 CSV，里面的中文绝对不会乱码
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"🎉 种子池构建完毕！")
    print(f"💾 结构化数据已安全保存至: {os.path.abspath(OUTPUT_CSV)}")
    print("💡 你现在可以直接用 Excel 打开它预览，或者直接喂给那个【全自动批量生成车间】脚本了！")


if __name__ == "__main__":
    create_seed_pool()