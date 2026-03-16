#!/usr/bin/env python3
"""
Anna's Archive Wikipedia URL Scraper
自动抓取 Wikipedia 页面上 Anna's Archive 的 URL 信息
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin


def fetch_wikipedia_page(url: str) -> str:
    """获取 Wikipedia 页面 HTML 内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_urls_from_infobox(html: str) -> list:
    """从右侧信息框中提取 URL"""
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    
    # 查找信息框 (infobox)
    infobox = soup.find('table', {'class': 'infobox'})
    
    if infobox:
        # 查找所有包含 URL 的行
        rows = infobox.find_all('tr')
        for row in rows:
            # 查找表头包含 "URL" 的行
            th = row.find('th')
            if th and 'URL' in th.get_text():
                # 查找该行中的所有链接
                td = row.find('td')
                if td:
                    links = td.find_all('a')
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        if href and href.startswith('http'):
                            urls.append({
                                'url': href,
                                'display_text': text
                            })
    
    return urls


def get_beijing_time() -> datetime:
    """获取当前北京时间（UTC+8）"""
    # 定义东八区时区
    beijing_tz = timezone(timedelta(hours=8))
    # 获取当前北京时间
    return datetime.now(beijing_tz)


def save_to_json(data: dict, filename: str = 'urls.json'):
    """保存数据为 JSON 格式"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存到 {filename}")


def save_to_markdown(data: dict, filename: str = 'urls.md'):
    """保存数据为 Markdown 格式"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Anna's Archive 网址列表\n\n")
        # 格式化北京时间显示（带时区标识）
        f.write(f"> 最后更新时间: {data['last_updated']}\n\n")
        f.write(f"> 数据来源: [{data['source']}]({data['source']})\n\n")
        
        f.write("## 主要网址\n\n")
        f.write("| 网址 | 显示文本 |\n")
        f.write("|------|----------|\n")
        
        for url_info in data['urls']:
            url = url_info.get('url', '')
            text = url_info.get('display_text', '')
            f.write(f"| [{url}]({url}) | {text} |\n")
      
        f.write("\n---\n\n")
        f.write("## 说明\n\n")
        f.write("此文件由自动化脚本生成，每天北京时间 08:00 自动从 Wikipedia 获取最新信息。\n")
    
    print(f"✓ 已保存到 {filename}")


def main():
    """主函数"""
    wiki_url = "https://en.wikipedia.org/wiki/Anna%27s_Archive"
    
    print(f"正在抓取: {wiki_url}")
    
    try:
        # 获取页面内容
        html = fetch_wikipedia_page(wiki_url)
        
        # 提取 URL
        urls = extract_urls_from_infobox(html)
        
        # 获取当前北京时间（带时区信息，格式友好）
        beijing_time = get_beijing_time()
        # 格式化输出：YYYY-MM-DD HH:MM:SS CST
        formatted_time = beijing_time.strftime("%Y-%m-%d %H:%M:%S CST")
        
        # 构建数据
        data = {
            'last_updated': formatted_time,
            'source': wiki_url,
            'urls': urls
        }
        
        # 保存文件
        save_to_json(data, 'urls.json')
        save_to_markdown(data, 'urls.md')
        
        print(f"\n抓取完成!")
        print(f"找到 {len(urls)} 个主要 URL")
        print(f"更新时间（北京时间）: {formatted_time}")
        
        # 打印结果
        print("\n抓取结果:")
        for url_info in urls:
            print(f"   - {url_info['url']} ({url_info.get('display_text', 'N/A')})")
        
    except requests.RequestException as e:
        print(f"网络请求失败: {e}")
        raise
    except Exception as e:
        print(f"处理失败: {e}")
        raise


if __name__ == '__main__':
    main()
