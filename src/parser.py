"""Parser functions to extract job data from HTML."""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


def parse_job_listings(html_content: str) -> List[Any]:
    """
    Parse job listing cards from Naukri.com HTML.
    
    Args:
        html_content: HTML content of the search results page
        
    Returns:
        List of BeautifulSoup job card elements
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Naukri.com uses div.srp-jobtuple-wrapper for job cards (verified via debugging)
    job_cards = []
    
    # Strategy 1: srp-jobtuple-wrapper (primary - confirmed working)
    job_cards = soup.select('div.srp-jobtuple-wrapper')
    if job_cards:
        return job_cards
    
    # Strategy 2: Try article.jobTuple (legacy/fallback)
    job_cards = soup.select('article.jobTuple')
    if job_cards:
        return job_cards
    
    # Strategy 3: Try any div with "tuple" in class
    job_cards = soup.select('div[class*="tuple"]')
    if job_cards and len(job_cards) > 5:
        return job_cards
    
    return []


def _clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and normalize text."""
    if not text:
        return None
    
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned if cleaned else None


def _extract_experience(exp_text: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """
    Extract min and max experience from text like '3-5 Yrs' or '2-3 years'.
    
    Returns:
        Tuple of (min_experience, max_experience) in years
    """
    if not exp_text:
        return None, None
    
    # Look for pattern like "3-5" or "2-3"
    match = re.search(r'(\d+)\s*-\s*(\d+)', exp_text)
    
    if match:
        try:
            return int(match.group(1)), int(match.group(2))
        except ValueError:
            pass
    
    # Look for single number like "3 Yrs" or "5+ years"
    match = re.search(r'(\d+)', exp_text)
    if match:
        try:
            exp = int(match.group(1))
            return exp, exp
        except ValueError:
            pass
    
    return None, None


def _extract_job_id(job_card: Any, job_url: Optional[str]) -> Optional[str]:
    """Extract job ID from card attributes or URL."""
    # Try data-job-id attribute
    job_id = job_card.get('data-job-id') or job_card.get('data-id')
    
    if job_id:
        return str(job_id)
    
    # Try to extract from URL
    if job_url:
        match = re.search(r'job-listings-(\d+)', job_url)
        if match:
            return match.group(1)
        
        match = re.search(r'/(\d+)$', job_url)
        if match:
            return match.group(1)
    
    return None


def extract_job_details(job_card: Any, base_url: str) -> Optional[Dict[str, Any]]:
    """
    Extract detailed job information from a job card element.
    
    Args:
        job_card: BeautifulSoup element representing a job card
        base_url: Base URL for constructing absolute URLs
        
    Returns:
        Dictionary containing job details or None if extraction failed
    """
    try:
        # Extract job title - try multiple selectors
        title_elem = (
            job_card.select_one('a.title') or
            job_card.select_one('.title a') or
            job_card.select_one('[class*="jobTitle"] a') or
            job_card.select_one('h2 a') or
            job_card.select_one('h3 a') or
            job_card.select_one('.title') or
            job_card.select_one('[class*="title"]')
        )
        
        # If no title elem found, try first link in card that looks like a job link
        if not title_elem:
            for link in job_card.select('a'):
                href = link.get('href', '')
                if 'job-listings' in href or 'jd' in href:
                    title_elem = link
                    break
        
        title = _clean_text(title_elem.get_text()) if title_elem else None
        
        # Extract job URL
        link_elem = title_elem if title_elem and title_elem.name == 'a' else job_card.select_one('a')
        job_url = None
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            job_url = href if href.startswith('http') else f'{base_url}{href}'
        
        # If we don't have at least a title, skip this card
        if not title:
            print(f'⚠ Skipping job card: no title found')
            return None
        
        # Extract job ID
        job_id = _extract_job_id(job_card, job_url)
        
        # Extract company name - try multiple patterns
        company_elem = (
            job_card.select_one('.companyName') or
            job_card.select_one('[class*="company"]') or
            job_card.select_one('.comp-name')
        )
        company_name = _clean_text(company_elem.get_text()) if company_elem else None
        
        # Extract experience - try multiple patterns
        exp_elem = (
            job_card.select_one('.expwdth') or
            job_card.select_one('[class*="exp"]') or
            job_card.select_one('.experience')
        )
        exp_text = _clean_text(exp_elem.get_text()) if exp_elem else None
        experience_min, experience_max = _extract_experience(exp_text)
        
        # Extract salary
        salary_elem = job_card.select_one('.salary, [class*="salary"], .sal-wrap')
        salary = _clean_text(salary_elem.get_text()) if salary_elem else None
        if salary and 'not disclosed' in salary.lower():
            salary = None
        
        # Extract location
        location_elem = (
            job_card.select_one('.locWdth') or
            job_card.select_one('[class*="loc"]') or
            job_card.select_one('.location')
        )
        location = _clean_text(location_elem.get_text()) if location_elem else None
        
        # Extract skills
        skills_elems = job_card.select('.tag, [class*="tag"], [class*="skill"], .chip')
        skills = []
        if skills_elems:
            for skill_elem in skills_elems:
                skill = _clean_text(skill_elem.get_text())
                if skill and len(skill) < 50:  # Avoid long text blocks
                    skills.append(skill)
        
        # Extract job description
        desc_elem = job_card.select_one('.jobDescription, [class*="desc"], .job-desc')
        job_description = _clean_text(desc_elem.get_text()) if desc_elem else None
        
        # Build job data object
        job_data = {
            'jobId': job_id,
            'title': title,
            'companyName': company_name,
            'salary': salary,
            'experienceMin': experience_min,
            'experienceMax': experience_max,
            'location': location,
            'skills': skills if skills else None,
            'jobDescription': job_description,
            'jobUrl': job_url
        }
        
        # Log what we extracted
        print(f'✓ Extracted: {title} at {company_name or "?"} | {location or "?"}')
        
        return job_data
    
    except Exception as e:
        print(f'❌ Error extracting job details: {e}')
        return None
