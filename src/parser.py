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
    
    # Try multiple selector strategies for Naukri.com job cards
    job_cards = []
    
    # Strategy 1: article.jobTuple (primary selector)
    job_cards = soup.select('article.jobTuple')
    if job_cards:
        return job_cards
    
    # Strategy 2: Try article tags with class containing 'job' or 'tuple'
    job_cards = soup.select('article[class*="job"]') or soup.select('article[class*="tuple"]')
    if job_cards:
        return job_cards
    
    # Strategy 3: Try div containers with job-related classes
    job_cards = soup.select('div.srp-jobtuple-wrapper article') or soup.select('div.jobTuple')
    if job_cards:
        return job_cards
    
    # Strategy 4: Look for any article tags (last resort)
    job_cards = soup.select('article')
    if job_cards and len(job_cards) > 5:  # Only if we find multiple (likely job listings)
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
        # Extract job title
        title_elem = job_card.select_one('.title, .jobTitle, a.title, .title-ellipsis')
        title = _clean_text(title_elem.get_text()) if title_elem else None
        
        # Extract job URL
        link_elem = job_card.select_one('a.title, a.jobTitle, .title a') or title_elem
        job_url = None
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            job_url = href if href.startswith('http') else f'{base_url}{href}'
        
        # Extract job ID
        job_id = _extract_job_id(job_card, job_url)
        
        # Extract company name
        company_elem = job_card.select_one('.companyName, .comp-name, .company-name, a.comp-name')
        company_name = _clean_text(company_elem.get_text()) if company_elem else None
        
        # Extract experience
        exp_elem = job_card.select_one('.experience, .expwdth, .exp-wrap')
        exp_text = _clean_text(exp_elem.get_text()) if exp_elem else None
        experience_min, experience_max = _extract_experience(exp_text)
        
        # Extract salary
        salary_elem = job_card.select_one('.salary, .salaryInfo, .sal-wrap')
        salary = _clean_text(salary_elem.get_text()) if salary_elem else None
        
        # Clean salary text
        if salary and 'not disclosed' in salary.lower():
            salary = None
        
        # Extract location
        location_elem = job_card.select_one('.location, .locWdth, .loc-wrap, .locationInfo')
        location = _clean_text(location_elem.get_text()) if location_elem else None
        
        # Extract skills
        skills_elems = job_card.select('.tag, .skill-tag, .tags span, .chip')
        skills = []
        
        if skills_elems:
            for skill_elem in skills_elems:
                skill = _clean_text(skill_elem.get_text())
                if skill:
                    skills.append(skill)
        
        # If no skills found with tags, try to extract from description
        if not skills:
            desc_elem = job_card.select_one('.jobDescription, .job-description, .desc')
            if desc_elem:
                desc_text = _clean_text(desc_elem.get_text())
                # Look for common skill keywords
                skill_keywords = [
                    'python', 'java', 'javascript', 'react', 'angular', 'node',
                    'aws', 'docker', 'kubernetes', 'sql', 'mongodb', 'postgresql',
                    'machine learning', 'ai', 'data science', 'devops', 'ci/cd'
                ]
                
                if desc_text:
                    desc_lower = desc_text.lower()
                    for keyword in skill_keywords:
                        if keyword in desc_lower:
                            skills.append(keyword.title())
        
        # Extract job description
        desc_elem = job_card.select_one('.jobDescription, .job-description, .desc, .job-desc')
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
        
        # Only return if we have at least title and company
        if title and company_name:
            return job_data
        
        return None
    
    except Exception as e:
        print(f'Error extracting job details: {e}')
        return None
