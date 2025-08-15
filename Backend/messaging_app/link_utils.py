import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def extract_urls_from_text(text):
    """Extract URLs from text content"""
    if not text:
        return []
    
    # Enhanced URL regex pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    
    # Validate URLs
    validator = URLValidator()
    valid_urls = []
    
    for url in urls:
        try:
            validator(url)
            valid_urls.append(url)
        except ValidationError:
            continue
    
    return valid_urls

def fetch_link_preview(url, timeout=10):
    """Fetch link preview data from URL"""
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract preview data
        preview_data = {
            'url': url,
            'title': '',
            'description': '',
            'image_url': '',
            'domain': urlparse(url).netloc
        }
        
        # Get title
        title_tag = soup.find('title')
        if title_tag:
            preview_data['title'] = title_tag.get_text().strip()
        
        # Try Open Graph tags first (Facebook, Twitter, etc.)
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            preview_data['title'] = og_title['content'].strip()
        
        og_description = soup.find('meta', property='og:description')
        if og_description and og_description.get('content'):
            preview_data['description'] = og_description['content'].strip()
        
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']
            # Make relative URLs absolute
            if image_url.startswith('/'):
                image_url = urljoin(url, image_url)
            preview_data['image_url'] = image_url
        
        # Fallback to Twitter Card tags
        if not preview_data['title']:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                preview_data['title'] = twitter_title['content'].strip()
        
        if not preview_data['description']:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc and twitter_desc.get('content'):
                preview_data['description'] = twitter_desc['content'].strip()
            else:
                # Fallback to meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    preview_data['description'] = meta_desc['content'].strip()
        
        if not preview_data['image_url']:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image['content']
                if image_url.startswith('/'):
                    image_url = urljoin(url, image_url)
                preview_data['image_url'] = image_url
        
        # Truncate fields to fit database constraints
        preview_data['title'] = preview_data['title'][:500] if preview_data['title'] else ''
        preview_data['description'] = preview_data['description'][:1000] if preview_data['description'] else ''
        
        logger.info(f"Successfully fetched preview for {url}: {preview_data['title']}")
        return preview_data
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch preview for {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error processing link preview for {url}: {str(e)}")
        return None

def create_link_previews_for_message(message):
    """Create link preview objects for a message"""
    from .models import LinkPreview
    
    if not message.content:
        return []
    
    urls = extract_urls_from_text(message.content)
    link_previews = []
    
    for url in urls:
        # Check if preview already exists for this URL and message
        existing_preview = LinkPreview.objects.filter(message=message, url=url).first()
        if existing_preview:
            link_previews.append(existing_preview)
            continue
        
        # Fetch preview data
        preview_data = fetch_link_preview(url)
        if preview_data:
            try:
                link_preview = LinkPreview.objects.create(
                    message=message,
                    url=preview_data['url'],
                    title=preview_data['title'],
                    description=preview_data['description'],
                    image_url=preview_data['image_url'],
                    domain=preview_data['domain']
                )
                link_previews.append(link_preview)
                logger.info(f"Created link preview for {url}")
            except Exception as e:
                logger.error(f"Failed to create link preview for {url}: {str(e)}")
    
    return link_previews
