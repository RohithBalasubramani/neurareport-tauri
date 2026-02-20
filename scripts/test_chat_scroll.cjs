const { chromium } = require('playwright');

const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  console.log('--- Navigating to chat-create page ---');
  await page.goto(`${BASE}/templates/new/chat`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Screenshot initial state
  await page.screenshot({ path: '/tmp/chat_scroll_2_fixed.png', fullPage: false });
  console.log('Screenshot saved (viewport only)');

  // Full page for comparison
  await page.screenshot({ path: '/tmp/chat_scroll_2_fullpage.png', fullPage: true });
  console.log('Full page screenshot saved');

  // Page scroll check
  const pageInfo = await page.evaluate(() => ({
    docH: document.documentElement.scrollHeight,
    viewH: window.innerHeight,
    scrollable: document.documentElement.scrollHeight > window.innerHeight,
  }));
  console.log('\n--- Page scroll ---');
  console.log(`  docH=${pageInfo.docH} viewH=${pageInfo.viewH} scrollable=${pageInfo.scrollable}`);

  // Scrollable containers
  const scrollables = await page.evaluate(() => {
    const all = document.querySelectorAll('*');
    const results = [];
    for (const el of all) {
      const style = window.getComputedStyle(el);
      if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
        const rect = el.getBoundingClientRect();
        if (rect.height > 50) {
          results.push({
            tag: el.tagName,
            height: Math.round(rect.height),
            top: Math.round(rect.top),
            scrollH: el.scrollHeight,
            clientH: el.clientHeight,
            scrollable: el.scrollHeight > el.clientHeight,
            overflowY: style.overflowY,
            text: el.textContent?.substring(0, 50),
          });
        }
      }
    }
    return results;
  });

  console.log('\n--- Scrollable containers ---');
  scrollables.forEach(s => {
    console.log(`  ${s.tag} h=${s.height} top=${s.top} scrollH=${s.scrollH} scrollable=${s.scrollable}`);
    console.log(`    text: ${s.text}`);
  });

  // Check chat editor container specifically
  const chatInfo = await page.evaluate(() => {
    const headers = document.querySelectorAll('*');
    for (const h of headers) {
      if (h.textContent?.trim() === 'AI Template Creator' && h.tagName.match(/H|SPAN|P|DIV/)) {
        // Walk up to find the flex column container
        let el = h;
        for (let i = 0; i < 15; i++) {
          el = el.parentElement;
          if (!el) break;
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          if (style.display === 'flex' && style.flexDirection === 'column' && rect.height > 100 && style.overflow === 'hidden') {
            return {
              found: true,
              height: Math.round(rect.height),
              top: Math.round(rect.top),
              bottom: Math.round(rect.bottom),
              overflow: style.overflow,
              minHeight: style.minHeight,
              inViewport: rect.bottom <= window.innerHeight,
            };
          }
        }
      }
    }
    return { found: false };
  });
  console.log('\n--- Chat editor container ---');
  console.log(chatInfo);

  // Check buttons
  const buttons = await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    return Array.from(btns)
      .filter(b => ['Back', 'Create Template', 'Apply Changes', 'Request Different Changes'].some(t => b.textContent?.includes(t)))
      .map(b => ({
        text: b.textContent?.trim(),
        visible: b.offsetParent !== null,
        rect: (() => { const r = b.getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom) }; })(),
        inViewport: (() => { const r = b.getBoundingClientRect(); return r.top >= 0 && r.bottom <= window.innerHeight; })(),
      }));
  });
  console.log('\n--- Key buttons ---');
  buttons.forEach(b => console.log(`  "${b.text}" visible=${b.visible} inViewport=${b.inViewport} top=${b.rect.top} bottom=${b.rect.bottom}`));

  // Check the input field
  const inputInfo = await page.evaluate(() => {
    const inputs = document.querySelectorAll('textarea, input[type="text"]');
    for (const inp of inputs) {
      if (inp.placeholder?.includes('Describe')) {
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

  await browser.close();
  console.log('\nDone.');
})();
