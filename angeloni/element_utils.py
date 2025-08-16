from typing import List, Optional
from playwright.async_api import Page, ElementHandle

class ElementUtils:
    """
    Utility functions for element finding and text extraction.
    """
    
    @staticmethod
    async def find_element(page: Page, selectors: List[str], timeout: int = 3000) -> Optional[ElementHandle]:
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
    async def extract_text(element: ElementHandle, selectors: List[str]) -> Optional[str]:
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
    
    @staticmethod
    async def find_elements(page: Page, selectors: List[str]) -> List[ElementHandle]:
        """
        Find all matching elements from a list of selectors.
        """
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                return elements
        return []