from bs4 import BeautifulSoup
from urllib.parse import urljoin

def parse_html(html: str, base_url: str = '') -> dict:
    """Extrae título, enlaces, metadatos, estructura y recursos de una página HTML."""
    soup = BeautifulSoup(html, 'lxml')

    title = soup.title.string.strip() if soup.title and soup.title.string else ''
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
    metas = {}
    for m in soup.find_all('meta'):
        if m.get('name') in ('description', 'keywords'):
            metas[m['name']] = m.get('content', '')
        elif m.get('property', '').startswith('og:'):
            metas[m['property']] = m.get('content', '')
    headers = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    images = [urljoin(base_url, img['src']) for img in soup.find_all('img', src=True)]

    return {
        'title': title, 
        'links': links,
        'meta_tags': metas,
        'structure': headers,
        'images_count': len(images),
    }
