from typing import List, Optional
from playwright.async_api import Page


class ElementUtils:
    """
    Utility functions for element finding and text extraction.
    """
    
    @staticmethod
    async def find_element(page: Page, selectors: List[str], timeout: int) -> Optional[any]:
        """
        Find the first matching element from a list of selectors.
        """
        for selector in selectors:
            try:
                return await page.wait_for_selector(selector, timeout=timeout)
            except:
                continue
        return None
    
    @staticmethod
    async def extract_text(element, selectors: List[str]) -> Optional[str]:
        """
        Extract text content from an element using multiple selector strategies.
        """
        if isinstance(selectors, str):
            selectors = [selectors]
            
        for selector in selectors:
            el = await element.query_selector(selector)
            if el:
                text = await el.text_content()
                if text and text.strip():
                    return text.strip()
        return None