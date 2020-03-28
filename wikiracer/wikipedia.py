from typing import List, Optional
from mediawiki import MediaWiki, MediaWikiPage, PageError, DisambiguationError  # type: ignore

WIKIPEDIA = MediaWiki(rate_limit=True)


def get_page(page: str) -> Optional[MediaWikiPage]:
    try:
        return WIKIPEDIA.page(page)
    except (PageError, DisambiguationError):
        return None


def get_random_page_name() -> str:
    print("Finding page with connections on Wikipedia...")
    while True:
        name = WIKIPEDIA.random(1)
        try:
            page = get_page(name)
            if page is not None and len(page.links) >= 2 and len(page.backlinks) >= 2:
                print("Done!")
                return name
        except DisambiguationError:
            continue


def get_forward_links(page: MediaWikiPage) -> List[str]:
    return page.links


def get_backward_links(page: MediaWikiPage) -> List[str]:
    return page.backlinks
