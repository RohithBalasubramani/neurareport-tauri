const { chromium } = require('playwright');

const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  console.log('--- Navigating to chat-create page ---');
  await page.goto(`${BASE}/templates/new/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Page scroll check
  const pageInfo = await page.evaluate(() => ({
    docH: document.documentElement.scrollHeight,
    viewH: window.innerHeight,
    scrollable: document.documentElement.scrollHeight > window.innerHeight,
  }));
  console.log(`Page: docH=${pageInfo.docH} viewH=${pageInfo.viewH} scrollable=${pageInfo.scrollable}`);

  // Find the chat messages scrollable container
  const chatScrollInfo = await page.evaluate(() => {
    // The messages area should be the one with overflow:auto inside the chat editor
    const allBoxes = document.querySelectorAll('*');
    const results = [];
    for (const el of allBoxes) {
      const style = window.getComputedStyle(el);
      if ((style.overflowY === 'auto' || style.overflow === 'auto') && el.getBoundingClientRect().height > 100) {
        const rect = el.getBoundingClientRect();
        const text = el.textContent?.substring(0, 60) || '';
        // Check if this is inside the chat panel (has "AI Template Creator" nearby)
        if (text.includes('Template Creator') || text.includes('Describe the report')) {
          results.push({
            height: Math.round(rect.height),
            top: Math.round(rect.top),
            bottom: Math.round(rect.bottom),
            scrollH: el.scrollHeight,
            clientH: el.clientHeight,
            canScroll: el.scrollHeight > el.clientHeight,
            inViewport: rect.bottom <= window.innerHeight,
          });
        }
      }
    }
    return results;
  });
  console.log('\n--- Chat scrollable areas ---');
  chatScrollInfo.forEach((s, i) => {
    console.log(`  [${i}] h=${s.height} top=${s.top} bottom=${s.bottom} scrollH=${s.scrollH} canScroll=${s.canScroll} inViewport=${s.inViewport}`);
  });

  // Check the chat input
  const inputInfo = await page.evaluate(() => {
    const inputs = document.querySelectorAll('textarea, input[type="text"]');
    for (const inp of inputs) {
      if (inp.placeholder?.includes('Describe') || inp.placeholder?.includes('report template')) {
        const r = inp.getBoundingClientRect();
        return {
          placeholder: inp.placeholder,
          top: Math.round(r.top),
          bottom: Math.round(r.bottom),
          inViewport: r.top >= 0 && r.bottom <= window.innerHeight,
        };
      }
    }
    return null;
  });
  console.log('\n--- Chat input ---');
  console.log(inputInfo);

  // Check Save Template button
  const saveBtn = await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent?.includes('Save Template')) {
        const r = b.getBoundingClientRect();
        return {
          text: b.textContent.trim(),
          top: Math.round(r.top),
          bottom: Math.round(r.bottom),
          inViewport: r.top >= 0 && r.bottom <= window.innerHeight,
          disabled: b.disabled,
        };
      }
    }
    return null;
  });
  console.log('\n--- Save Template button ---');
  console.log(saveBtn);

  // Screenshot
  await page.screenshot({ path: '/tmp/chat_buttons_test.png', fullPage: false });
  console.log('\nScreenshot saved to /tmp/chat_buttons_test.png');

  await browser.close();
  console.log('Done.');
})();
