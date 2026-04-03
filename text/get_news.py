import os
import time
import requests
from bs4 import BeautifulSoup
import trafilatura

# ================= 配置区 =================
# 列表页基础 URL，{} 是用来占位替换页码的
BASE_LIST_URL = "https://suanpanmall.com/news-center/{}"
# 创建一个专门存放纯净语料的文件夹
CORPUS_DIR = "suanpan_news_corpus"
os.makedirs(CORPUS_DIR, exist_ok=True)

# 伪装成正常的浏览器，防止被自家官网的防火墙拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ==========================================

def get_all_article_links(start_page, end_page):
    """第一阶段：从列表页提取所有新闻详情的链接"""
    print(f"🔍 第一阶段：正在扫描第 {start_page} 到 {end_page} 页的新闻列表...")
    article_links = set()  # 使用集合自动去重

    for page in range(start_page, end_page + 1):
        url = BASE_LIST_URL.format(page)
        print(f"   -> 正在获取列表页: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'  # 确保中文不乱码
            soup = BeautifulSoup(response.text, 'html.parser')

            # ================= 🌟 极其关键的一步 =================
            # 找到页面中所有的 <a> 标签
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 【你需要在这里修改过滤规则！】
                # 假设真实的新闻详情链接里都包含 "news_detail" 或 "article" 等字眼
                # 你需要打开官网看一眼真实详情页的链接长什么样，然后替换这里的判断条件
                if "%" in href and len(href) > 20:

                    # 处理相对路径 (如果 href 是 /news-center/123.html)
                    if href.startswith('/'):
                        full_link = "https://suanpanmall.com" + href
                    # 处理带域名的绝对路径
                    elif href.startswith('http'):
                        full_link = href
                    else:
                        full_link = "https://suanpanmall.com/" + href

                    article_links.add(full_link)
            # =======================================================

        except Exception as e:
            print(f"❌ 请求列表页第 {page} 页失败: {str(e)}")

        time.sleep(1)  # 礼貌爬取，每翻一页休息1秒

    return list(article_links)


def batch_download_articles(links):
    """第二阶段：批量下载并提取纯净正文"""
    print(f"\n🚀 第二阶段：开始批量收割！共发现 {len(links)} 篇新闻。")

    for index, link in enumerate(links):
        print(f"   [{index + 1}/{len(links)}] 正在提取: {link}")

        downloaded = trafilatura.fetch_url(link)
        if downloaded:
            article_text = trafilatura.extract(
                downloaded,
                include_links=False,
                include_images=False,
                include_formatting=True
            )

            if article_text:
                # 生成安全的文件名 (用序号命名，避免标题里有特殊字符无法保存)
                file_path = os.path.join(CORPUS_DIR, f"news_corpus_{index + 1}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    # 在开头悄悄写入原文链接，方便 Dify 溯源
                    f.write(f"【信息来源】：{link}\n\n")
                    f.write(article_text)
            else:
                print("      ⚠️ 提取失败：页面可能是图片、视频，或结构特殊无法解析。")
        else:
            print("      ❌ 下载网页失败：可能请求超时或被拦截。")

        time.sleep(1.5)  # 每扒一篇文章休息 1.5 秒，保护服务器


# ================= 主控制台 =================
if __name__ == "__main__":
    # 抓取第 1 页到第 3 页
    links = get_all_article_links(1, 3)

    if links:
        batch_download_articles(links)
        print(f"\n🎉 完美收工！所有纯净语料已存入文件夹：{os.path.abspath(CORPUS_DIR)}")
        print("💡 你现在可以把这个文件夹里的 txt 文件全选，一把拖进 Dify 知识库了！")
    else:
        print("\n🤔 没有找到任何新闻链接。请检查代码中【过滤规则】是否符合实际情况。")