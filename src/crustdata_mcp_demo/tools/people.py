from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

from crustdata_mcp_demo.server import mcp
from crustdata_mcp_demo.client import build_request


class EnrichPersonInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    linkedin_urls: List[str] = Field(
        ...,
        description="List of LinkedIn profile URLs to enrich",
        min_length=1,
        max_length=25,
    )


class GetSocialPostsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    person_linkedin_url: str = Field(
        ...,
        description="LinkedIn profile URL of the person",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination (20 posts per page)",
    )


class PersonSearchFilter(BaseModel):
    model_config = ConfigDict(extra="allow")

    filter_type: str = Field(
        ...,
        description="Filter type (e.g. 'CURRENT_COMPANY', 'CURRENT_TITLE', 'SENIORITY_LEVEL', 'INDUSTRY')",
    )
    type: str = Field(
        ...,
        description="Operation type: 'in' or 'not in'",
    )
    value: Any = Field(
        ...,
        description="Filter value(s) as a list",
    )


class SearchPeopleInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filters: List[PersonSearchFilter] = Field(
        ...,
        description="List of search filters (combined with AND logic)",
        min_length=1,
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination (25 results per page)",
    )


@mcp.tool(
    name="crustdata_enrich_person",
    annotations={
        "title": "Enrich Person",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_enrich_person(params: EnrichPersonInput) -> str:
    """
    Enrich LinkedIn profiles with detailed professional data.
    
    Retrieves comprehensive info including employment history, education,
    skills, connections, and more for one or more LinkedIn profiles.
    
    Args:
        params: EnrichPersonInput containing:
            - linkedin_urls: List of LinkedIn profile URLs
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Note: If a profile isn't found, Crustdata auto-enriches it within 30-60 min.
    Query again after that time to get the data.
    
    Example URLs:
        'https://www.linkedin.com/in/satyanadella/'
        'https://www.linkedin.com/in/jeffweiner08/'
    """
    result = build_request(
        method="GET",
        path="/screener/person/enrich",
        params={"linkedin_profile_url": ",".join(params.linkedin_urls)},
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_get_social_posts",
    annotations={
        "title": "Get Social Posts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_get_social_posts(params: GetSocialPostsInput) -> str:
    """
    Get recent social media posts and engagement metrics for a person.
    
    Returns posts with content, reactions, comments, shares, and info
    about people who interacted with the posts.
    
    Args:
        params: GetSocialPostsInput containing:
            - person_linkedin_url: LinkedIn profile URL
            - page: Page number (20 posts per page)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Note: This endpoint fetches data in real-time. Expect 30-60 second latency.
    """
    result = build_request(
        method="GET",
        path="/screener/social_posts",
        params={
            "person_linkedin_url": params.person_linkedin_url,
            "page": params.page,
        },
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_search_people",
    annotations={
        "title": "Search People",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_search_people(params: SearchPeopleInput) -> str:
    """
    Search for professional profiles using structured filters.
    
    Find people by company, title, seniority, industry, location, skills, etc.
    Filters are combined with AND logic. Returns 25 results per page.
    
    Args:
        params: SearchPeopleInput containing:
            - filters: List of filter objects with filter_type, type, value
            - page: Page number (starts at 1)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Filter types:
        CURRENT_COMPANY: Company names
        CURRENT_TITLE: Job titles
        PAST_TITLE: Previous job titles
        PAST_COMPANY: Previous employers
        SENIORITY_LEVEL: ['Owner / Partner', 'CXO', 'Vice President', 'Director', 
                          'Experienced Manager', 'Entry Level Manager', 'Strategic', 
                          'Senior', 'Entry Level', 'In Training']
        INDUSTRY: Industry names
        REGION: Geographic regions
        COMPANY_HEADCOUNT: ['Self-employed', '1-10', '11-50', '51-200', '201-500', 
                            '501-1,000', '1,001-5,000', '5,001-10,000', '10,001+']
        YEARS_AT_CURRENT_COMPANY: ['Less than 1 year', '1 to 2 years', '3 to 5 years', 
                                    '6 to 10 years', 'More than 10 years']
        YEARS_OF_EXPERIENCE: Same values as above
        FUNCTION: Department/function names
        KEYWORD: Keywords to search for
        COMPANY_TYPE: ['Public Company', 'Privately Held', 'Non Profit', etc.]
    
    Boolean filters (no value needed, just filter_type):
        POSTED_ON_SOCIAL_MEDIA, RECENTLY_CHANGED_JOBS, IN_THE_NEWS
    """
    body = {
        "filters": [f.model_dump(exclude_none=True) for f in params.filters],
        "page": params.page,
    }
    
    result = build_request(
        method="POST",
        path="/screener/person/search",
        json_body=body,
    )
    
    return result.format_output()
