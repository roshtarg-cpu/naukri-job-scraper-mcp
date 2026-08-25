"""Utility functions for fetching and processing data."""

import asyncio
from typing import Optional
from urllib.parse import urlparse
from camoufox.async_api import AsyncCamoufox


def _parse_proxy(proxy_url: Optional[str]) -> Optional[dict]:
    """
    Parse Apify proxy URL into Camoufox proxy configuration.
    
    Args:
        proxy_url: Proxy URL in format http://user:pass@host:port
        
    Returns:
        Dictionary with proxy configuration or None
    """
    if not proxy_url:
        return None
    
    try:
        parsed = urlparse(proxy_url)
        
        proxy_config = {
            'server': f'{parsed.scheme}://{parsed.hostname}:{parsed.port}'
        }
        
        if parsed.username and parsed.password:
            proxy_config['username'] = parsed.username
            proxy_config['password'] = parsed.password
        
        return proxy_config
    
    except Exception as e:
        print(f'Error parsing proxy URL: {e}')
        return None


async def fetch_jobs_page(url: str, proxy_url: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
    """
    Fetch a Naukri.com jobs page using Camoufox browser automation.
    
    Args:
        url: The URL to fetch
        proxy_url: Optional proxy URL from Apify
        max_retries: Maximum number of retry attempts
        
    Returns:
        HTML content of the page or None if failed
    """
    proxy_config = _parse_proxy(proxy_url)
    
    for attempt in range(max_retries):
        try:
            # Use Camoufox with residential proxy and realistic fingerprinting
            async with AsyncCamoufox(
                headless=True,
                proxy=proxy_config,
                geoip=True,  # Use GeoIP to match proxy location
                humanize=True  # Add human-like behavior
            ) as browser:
                
                # Create a new page
                page = await browser.new_page()
                
                # Set realistic viewport
                await page.set_viewport_size({'width': 1920, 'height': 1080})
                
                # Navigate to the URL with network idle to ensure full load
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Wait for React/Next.js to hydrate and render job listings
                # Naukri loads job data via XHR after page load
                # Give it more time to replace shimmer placeholders with real jobs
                await asyncio.sleep(5)  # Increased from 3 to 5 seconds
                
                # Wait specifically for job listings to appear
                try:
                    # Wait for either article tags or job-related divs
                    await page.wait_for_selector(
                        'article, div.srp-jobtuple-wrapper, div[class*="job"]',
                        timeout=30000  # Increased from 20s to 30s
                    )
                    print('✓ Job content found')
                except Exception as e:
                    print(f'⚠ Timeout waiting for job content: {e}')
                    # Try scrolling to trigger lazy loading
                    await page.evaluate('window.scrollTo(0, 1000)')
                    await asyncio.sleep(3)  # More time after scroll
                
                # Get page content
                content = await page.content()
                
                await page.close()
                
                return content
        
        except Exception as e:
            print(f'Attempt {attempt + 1}/{max_retries} failed: {e}')
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                print(f'Retrying in {wait_time} seconds...')
                await asyncio.sleep(wait_time)
            else:
                print(f'All {max_retries} attempts failed for URL: {url}')
                return None
    
    return None
