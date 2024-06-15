import requests
from bs4 import BeautifulSoup
import re
import os
from tqdm import tqdm  # Use standard tqdm instead of tqdm_notebook
from urllib.parse import urljoin, urlparse

def download_images(url, save_path='images', start_index=0):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Không thể truy cập trang {url}: {e}")
        return start_index

    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all('img', src=True)
    total_images = len(image_tags)
    print(f'Tìm thấy {total_images} hình ảnh trong trang {url}')

    for i, image_tag in enumerate(tqdm(image_tags, desc="Tải xuống hình ảnh", total=total_images)):
        image_url = image_tag['src']
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        elif image_url.startswith('/'):
            image_url = urljoin(url, image_url)

        try:
            image_data = requests.get(image_url).content
            domain = urlparse(url).netloc.replace('.', '_')
            filename = f'{domain}_image_{start_index + i}.jpg'
            filepath = os.path.join(save_path, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
        except Exception as e:
            print(f"Lỗi tải hình ảnh {image_url}: {e}")

    return start_index + total_images

def crawl_website(base_url, save_path='images'):
    try:
        response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Không thể truy cập trang {base_url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = urljoin(base_url, href)
        elif not href.startswith('http'):
            href = urljoin(base_url, '/' + href)
        links.add(href)

    total_images_downloaded = 0
    for link in tqdm(links, desc="Duyệt qua trang con"):
        try:
            total_images_downloaded = download_images(link, save_path, start_index=total_images_downloaded)
        except Exception as e:
            print(f"Lỗi duyệt trang {link}: {e}")

if __name__ == '__main__':
    base_url = 'https://www.glamira.com/'
    save_path = 'glamira_images'
    crawl_website(base_url, save_path)
