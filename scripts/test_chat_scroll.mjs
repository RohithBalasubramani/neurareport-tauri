import { chromium } from 'playwright';

const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  console.log('--- Navigating to chat-create page ---');
  await page.goto(`${BASE}/templates/new/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Screenshot initial state
  await page.screenshot({ path: '/tmp/chat_scroll_1_initial.png', fullPage: true });
  console.log('Screenshot 1: initial state saved');

  // Check the grid layout
  const gridBox = await page.locator('[class*="MuiBox-root"]').filter({ has: page.locator('text=Template Preview') }).first().boundingBox();
  console.log('Grid/Preview container bounds:', gridBox);

  // Find the chat panel — it has "AI Template Creator" header
  const chatPanel = page.locator('text=AI Template Creator').locator('xpath=ancestor::div[contains(@class, "MuiBox-root")]').last();
  const chatBounds = await chatPanel.boundingBox();
  console.log('Chat panel bounds:', chatBounds);

  // Check if the messages area scrolls independently
  // Find the messages container (has overflow:auto)
  const allBoxes = await page.evaluate(() => {
    const boxes = document.querySelectorAll('[class*="MuiBox-root"]');
    const results = [];
    boxes.forEach((box, i) => {
      const style = window.getComputedStyle(box);
      if (style.overflow === 'auto' || style.overflowY === 'auto' || style.overflowY === 'scroll') {
        const rect = box.getBoundingClientRect();
        results.push({
          index: i,
          overflow: style.overflow,
          overflowY: style.overflowY,
          height: rect.height,
          top: rect.top,
          scrollHeight: box.scrollHeight,
          clientHeight: box.clientHeight,
          isScrollable: box.scrollHeight > box.clientHeight,
          textSnippet: box.textContent?.substring(0, 80),
        });
      }
    });
    return results;
  });
  console.log('\n--- Scrollable containers ---');
  allBoxes.forEach(b => {
    console.log(`  Box ${b.index}: overflow=${b.overflow}/${b.overflowY}, height=${b.height.toFixed(0)}, scrollHeight=${b.scrollHeight}, clientHeight=${b.clientHeight}, scrollable=${b.isScrollable}`);
    console.log(`    Text: ${b.textSnippet}`);
  });

  // Check the grid container height
  const gridInfo = await page.evaluate(() => {
    const grids = document.querySelectorAll('[class*="MuiBox-root"]');
    for (const g of grids) {
      const style = window.getComputedStyle(g);
      if (style.display === 'grid') {
        const rect = g.getBoundingClientRect();
        return {
          display: style.display,
          gridTemplateColumns: style.gridTemplateColumns,
          height: rect.height,
          minHeight: style.minHeight,
          maxHeight: style.maxHeight,
          overflow: style.overflow,
        };
      }
    }
    return null;
  });
  console.log('\n--- Grid container ---');
  console.log(gridInfo);

  // Check chat wrapper box (the one we added with fixed height)
  const chatWrapperInfo = await page.evaluate(() => {
    // Find the TemplateChatEditor root — it has border and "AI Template Creator"
    const headers = document.querySelectorAll('h6, [class*="MuiTypography-subtitle1"]');
    for (const h of headers) {
      if (h.textContent?.includes('AI Template Creator')) {
        // Walk up to find the outer container
        let el = h;
        for (let i = 0; i < 10; i++) {
          el = el.parentElement;
          if (!el) break;
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          if (rect.height > 200) {
            // Check if this is the flex column container
            if (style.display === 'flex' && style.flexDirection === 'column') {
              return {
                tag: el.tagName,
                height: rect.height,
                maxHeight: style.maxHeight,
                overflow: style.overflow,
                display: style.display,
                flexDirection: style.flexDirection,
                parentHeight: el.parentElement ? el.parentElement.getBoundingClientRect().height : null,
                parentMaxHeight: el.parentElement ? window.getComputedStyle(el.parentElement).maxHeight : null,
                parentMinHeight: el.parentElement ? window.getComputedStyle(el.parentElement).minHeight : null,
              };
            }
          }
        }
      }
    }
    return null;
  });
  console.log('\n--- Chat editor container ---');
  console.log(chatWrapperInfo);

  // Check overall page scroll
  const pageScroll = await page.evaluate(() => ({
    documentHeight: document.documentElement.scrollHeight,
    viewportHeight: window.innerHeight,
    isPageScrollable: document.documentElement.scrollHeight > window.innerHeight,
  }));
  console.log('\n--- Page scroll ---');
  console.log(pageScroll);

  await browser.close();
  console.log('\nDone.');
})();
