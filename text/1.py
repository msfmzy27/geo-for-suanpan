import os

# ================= 配置区 =================
CORPUS_DIR = "suanpan_news_corpus"  # 刚才存放 17 篇新闻的文件夹名
OUTPUT_FILE = "suanpan_merged_knowledge.txt"  # 最终输出的超级文档名字


# ==========================================

def clean_and_merge_corpus():
    print(f"🧹 开始扫描目录: {CORPUS_DIR}")

    if not os.path.exists(CORPUS_DIR):
        print("❌ 找不到文件夹，请检查名字是否正确。")
        return

    all_files = [f for f in os.listdir(CORPUS_DIR) if f.endswith(".txt")]
    print(f"📦 共发现 {len(all_files)} 个独立语料文件。正在执行清洗和聚合...")

    merged_content = []

    for index, filename in enumerate(all_files):
        filepath = os.path.join(CORPUS_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            # ✂️ 核心清洗逻辑：遇到带有“信息来源”的行，直接跳过不录入
            if line.strip().startswith("【信息来源】"):
                continue
            clean_lines.append(line)

        # 拼接清洗后的单篇文章文本
        article_text = "".join(clean_lines).strip()

        # 为了防止不同文章的内容粘连，我们在每篇文章之间加入醒目的分割线
        # 这也能帮助 Dify 更好地识别上下文边界
        merged_content.append(f"\n\n================ [第 {index + 1} 篇官方资讯] ================\n\n")
        merged_content.append(article_text)

    # 最终写入超级文档
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("".join(merged_content))

    print(f"\n🎉 聚合完成！17 篇文章已完美融合成一个文件。")
    print(f"💾 超级知识库文档已生成: {os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 预估总体积: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")


if __name__ == "__main__":
    clean_and_merge_corpus()
