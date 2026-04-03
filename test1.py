import requests
import html2text
import os


def web_to_markdown_local(url, save_name):
    print(f"🌐 正在请求网页: {url}")

    # 1. 模拟浏览器请求，防止被简单的反爬拦截
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        # 自动检测并设置网页编码（解决中文乱码的关键）
        response.encoding = response.apparent_encoding

        if response.status_code == 200:
            html_content = response.text
            print("✅ 网页抓取成功，开始本地转换...")

            # 2. 配置转换器
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = False  # 保留链接，GEO 优化需要参考链接
            text_maker.bypass_tables = False  # 保留表格，这对技术参数很重要
            text_maker.ignore_images = True  # 忽略图片，减少干扰
            text_maker.single_line_break = True  # 减少多余换行

            # 3. 执行转换
            markdown_text = text_maker.handle(html_content)

            # 4. 保存结果
            with open(save_name, "w", encoding="utf-8") as f:
                f.write(markdown_text)

            print(f"🎉 转换完成！文件已保存至: {os.path.abspath(save_name)}")
            return True
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 运行报错: {e}")
        return False


if __name__ == "__main__":
    # 测试
    target = "https://tantai.bio/about-us/"
    web_to_markdown_local(target, "tantai_business.md")
