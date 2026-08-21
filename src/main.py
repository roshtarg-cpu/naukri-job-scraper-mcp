"""Main entry point for Naukri.com Job Scraper actor."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from apify import Actor
from .utils import fetch_jobs_page
from .parser import parse_job_listings, extract_job_details


async def main() -> None:
    """Main actor function."""
    async with Actor:
        # Get input from Apify platform
        actor_input = await Actor.get_input() or {}
        
        # Extract input parameters with defaults
        search_query = actor_input.get('searchQuery', 'software engineer')
        location = actor_input.get('location', '')
        max_results = actor_input.get('maxResults', 50)
        
        Actor.log.info(f'Starting Naukri.com scraper')
        Actor.log.info(f'Search query: {search_query}')
        Actor.log.info(f'Location: {location or "All India"}')
        Actor.log.info(f'Max results: {max_results}')
        
        try:
            # Get residential proxy configuration
            proxy_config = await Actor.create_proxy_configuration(
                actor_proxy_input={'useApifyProxy': True, 'apifyProxyGroups': ['RESIDENTIAL']}
            )
            
            if not proxy_config:
                Actor.log.warning('Failed to create residential proxy, attempting without proxy')
                proxy_url = None
            else:
                proxy_url = await proxy_config.new_url()
                Actor.log.info(f'Using residential proxy')
            
            # Build search URL
            base_url = 'https://www.naukri.com'
            
            # Clean and format search query for URL
            query_slug = search_query.lower().replace(' ', '-')
            
            if location:
                location_slug = location.lower().replace(' ', '-')
                search_url = f'{base_url}/{query_slug}-jobs-in-{location_slug}'
            else:
                search_url = f'{base_url}/{query_slug}-jobs'
            
            Actor.log.info(f'Search URL: {search_url}')
            
            jobs_collected = 0
            page_num = 1
            max_pages = (max_results // 20) + 1  # Naukri shows ~20 jobs per page
            
            while jobs_collected < max_results and page_num <= max_pages:
                Actor.log.info(f'Scraping page {page_num}...')
                
                # Construct paginated URL
                if page_num == 1:
                    page_url = search_url
                else:
                    page_url = f'{search_url}-{page_num}'
                
                # Fetch the page
                html_content = await fetch_jobs_page(page_url, proxy_url)
                
                if not html_content:
                    Actor.log.warning(f'Failed to fetch page {page_num}, stopping')
                    break
                
                # Parse job listings from the page
                job_cards = parse_job_listings(html_content)
                
                if not job_cards:
                    Actor.log.info(f'No more jobs found on page {page_num}')
                    break
                
                Actor.log.info(f'Found {len(job_cards)} job listings on page {page_num}')
                
                # Process each job card
                for idx, job_card in enumerate(job_cards):
                    if jobs_collected >= max_results:
                        break
                    
                    try:
                        job_data = extract_job_details(job_card, base_url)
                        
                        if job_data:
                            # Add scraped timestamp
                            job_data['scrapedAt'] = datetime.now(timezone.utc).isoformat()
                            
                            # Push to dataset immediately
                            await Actor.push_data(job_data)
                            jobs_collected += 1
                            
                            Actor.log.info(
                                f'Job {jobs_collected}/{max_results}: {job_data.get("title")} '
                                f'at {job_data.get("companyName")}'
                            )
                    
                    except Exception as e:
                        Actor.log.exception(f'Error processing job card {idx + 1}: {e}')
                        continue
                
                # Add delay between pages to avoid rate limiting
                if jobs_collected < max_results and page_num < max_pages:
                    await asyncio.sleep(2)
                
                page_num += 1
            
            Actor.log.info(f'Scraping completed! Total jobs collected: {jobs_collected}')
        
        except Exception as e:
            Actor.log.exception(f'Actor failed with error: {e}')
            raise


if __name__ == '__main__':
    asyncio.run(main())
