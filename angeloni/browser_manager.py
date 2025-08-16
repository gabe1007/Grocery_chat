import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext
from .config import Config

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages browser lifecycle and context creation.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def initialize(self):
        """
        Initialize browser and context if not already done.
        """
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=self.config.browser_args
            )
            self.context = await self.browser.new_context(
                viewport=self.config.viewport,
                user_agent=self.config.user_agent
            )
            logger.info("Browser initialized")
    
    async def new_page(self):
        """
        Create a new page in the current context.
        """
        if not self.context:
            await self.initialize()
        return await self.context.new_page()
    
    async def close(self):
        """
        Close browser and clean up resources.
        """
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            logger.info("Browser closed")