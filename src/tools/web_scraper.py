"""Web scraping tool using Playwright."""

from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Browser, Page
import structlog

from .base import Tool, ToolResult, ToolConfig

logger = structlog.get_logger(__name__)


class WebScraperTool(Tool):
    """Web scraping tool with JavaScript support."""

    def __init__(self, config: ToolConfig):
        """Initialize web scraper tool.

        Args:
            config: Tool configuration
        """
        super().__init__(config)
        self.browser: Optional[Browser] = None
        self.logger = logger.bind(tool="web_scraper")

    async def execute(
        self,
        url: str,
        selectors: Dict[str, str] = None,
        wait_for: str = None,
        screenshot: bool = False,
        javascript: bool = True,
    ) -> ToolResult:
        """Scrape a website.

        Args:
            url: URL to scrape
            selectors: CSS selectors to extract data
            wait_for: Selector to wait for before scraping
            screenshot: Take a screenshot
            javascript: Enable JavaScript rendering

        Returns:
            Scraped data
        """
        try:
            self.logger.info("Scraping website", url=url)

            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox']
                )

                # Create page
                page = await browser.new_page()

                # Navigate to URL
                await page.goto(url, wait_until="networkidle")

                # Wait for specific element if requested
                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=30000)

                # Extract data using selectors
                data = {}
                if selectors:
                    for key, selector in selectors.items():
                        elements = await page.query_selector_all(selector)
                        if elements:
                            texts = []
                            for element in elements:
                                text = await element.inner_text()
                                texts.append(text)
                            data[key] = texts if len(texts) > 1 else texts[0]
                        else:
                            data[key] = None

                # Get page content
                html_content = await page.content()
                data['html'] = html_content
                data['title'] = await page.title()
                data['url'] = url

                # Take screenshot if requested
                if screenshot:
                    screenshot_bytes = await page.screenshot(full_page=True)
                    data['screenshot'] = screenshot_bytes

                await browser.close()

                return ToolResult(
                    success=True,
                    data=data,
                    metadata={'url': url, 'selectors_used': list(selectors.keys()) if selectors else []},
                )

        except Exception as e:
            self.logger.error("Web scraping failed", url=url, error=str(e))
            return ToolResult(
                success=False,
                error=f"Web scraping failed: {str(e)}",
            )





