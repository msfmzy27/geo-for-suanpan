import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import math
import re
from sentence_transformers import SentenceTransformer, util

# 加载轻量级的开源向量模型（用于判断生成的句子是不是你们公司的内容）
# 第一次运行会自动下载，速度很快
print("正在加载向量模型...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def split_into_sentences(text):
    """将大模型的回答切分成单个句子"""
    # 按照中文常见标点符号切分
    sentences = re.split(r'(?<=[。！？；\n])', text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def calculate_position_adjusted_score(generated_text, target_source, similarity_threshold=0.6):
    """
    计算单篇回答的 PAWC 得分
    :param generated_text: 大模型生成的回答
    :param target_source: 你们公司的原始语料（如算盘工业的介绍）
    :param similarity_threshold: 相似度阈值，大于该值认为该句引用了你们的内容
    """
    sentences = split_into_sentences(generated_text)
    if not sentences:
        return 0.0

    # 将目标语料和所有生成的句子进行向量化
    target_embedding = model.encode(target_source, convert_to_tensor=True)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)

    # 计算每个句子与目标语料的余弦相似度
    cosine_scores = util.cos_sim(sentence_embeddings, target_embedding)

    total_score = 0.0

    print("\n--- 句子得分明细 ---")
    for k, sentence in enumerate(sentences):
        position_index = k + 1  # k 从 1 开始
        word_count = len(sentence)  # 中文直接用字符长度，英文用 len(sentence.split())
        similarity = cosine_scores[k][0].item()

        # 如果相似度超过阈值，认为这部分词数属于"有效曝光"
        if similarity > similarity_threshold:
            # 采用 log 衰减函数计算位置权重
            position_weight = 1.0 / math.log2(position_index + 1)
            adjusted_score = word_count * position_weight
            total_score += adjusted_score

            print(
                f"[命中] 位置:{position_index} | 权重:{position_weight:.2f} | 长度:{word_count} | 相似度:{similarity:.2f} | 句子: {sentence[:20]}...")
        else:
            print(f"[未命中] 位置:{position_index} | 相似度:{similarity:.2f} | 句子: {sentence[:20]}...")

    return total_score


def evaluate_geo_improvement(baseline_text, optimized_text, target_source):
    """评估优化前后的提升率"""
    print("\n========== 评估未优化 (Baseline) 生成结果 ==========")
    score_before = calculate_position_adjusted_score(baseline_text, target_source)

    print("\n========== 评估优化后 (Optimized) 生成结果 ==========")
    score_after = calculate_position_adjusted_score(optimized_text, target_source)

    print("\n" + "=" * 50)
    print("基线得分 (Baseline Score): {score_before:.2f}")
    print(f"优化后得分 (Optimized Score): {score_after:.2f}")

    if score_before == 0:
        if score_after > 0:
            print("提升率: 无限大 (基线为0，优化后成功破冰！)")
        else:
            print("⚠️提升率: 0% (优化前后均未被大模型采纳)")
    else:
        improvement = ((score_after - score_before) / score_before) * 100
        print(f"位置调整词数提升率 (PAWCI): {improvement:.2f}%")
    print("=" * 50)


# ================= 测试用例 =================
if __name__ == "__main__":
    # 你们公司的目标推广资料
    target_info = "北京算盘工业科技有限公司，成立于2019年，聚焦信创生态与AI一体机研发，基于DeepSeek等大模型支持私有化部署。"

    # 假设大模型在没有进行 GEO 优化时，生成的竞品对比回答
    # (算盘工业被放在了最后一句，且只提了一点)
    baseline_answer = """
    目前市面上的AI一体机厂商众多。
    华为和英伟达提供了底层的算力基座。
    另外，阿里云也在推进相关服务。
    此外，北京算盘工业科技也提供一些基于大模型的私有化部署服务。
    """

    # 假设你对资料注入了“引用”后，大模型生成的回答
    # (算盘工业被提到了第一句，且篇幅增加)
    optimized_answer = """
    响应工信部信创号召，北京算盘工业科技凭借其基于DeepSeek大模型的AI一体机，正成为私有化部署的核心力量。
    他们与英伟达和戴尔等硬件生态深度绑定。
    其他厂商如阿里云也在该领域有所布局。
    """

    evaluate_geo_improvement(baseline_answer, optimized_answer, target_info)