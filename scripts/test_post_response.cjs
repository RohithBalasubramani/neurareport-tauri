const { chromium } = require('playwright');
const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  
  await page.goto(BASE + '/templates/new/chat', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);
  
  // The previous session should still be there (zustand persist)
  await page.screenshot({ path: '/tmp/post_response.png' });
  
  const s = await page.evaluate(() => {
    const docH = document.documentElement.scrollHeight;
    const viewH = window.innerHeight;
    
    const btns = Array.from(document.querySelectorAll('button'))
      .filter(b => ['Apply','Request Different','Save Template','Back','Show Preview'].some(k => b.textContent && b.textContent.includes(k)))
      .map(b => { const r = b.getBoundingClientRect(); return { t: b.textContent.trim().substring(0,30), top: Math.round(r.top), bot: Math.round(r.bottom), inView: r.top>=0 && r.bottom<=window.innerHeight }; });
    
    // Find scrollable chat area
    let chatInfo = null;
    document.querySelectorAll('*').forEach(el => {
      const cs = window.getComputedStyle(el);
      if ((cs.overflowY === 'auto' || cs.overflow === 'auto') && el.clientHeight > 80) {
        const r = el.getBoundingClientRect();
        if (el.scrollHeight > el.clientHeight + 10 && el.textContent && el.textContent.includes('NeuraReport')) {
          chatInfo = { h: Math.round(r.height), sH: el.scrollHeight, top: Math.round(r.top), bot: Math.round(r.bottom), scrollable: true };
        }
      }
    });
    
    // Preview area
    let previewH = null;
    const iframes = document.querySelectorAll('iframe');
    if (iframes.length > 0) {
      const r = iframes[0].getBoundingClientRect();
      previewH = { h: Math.round(r.height), w: Math.round(r.width), top: Math.round(r.top) };
    }
    
    return { docH, viewH, pageScroll: docH > viewH, btns, chatInfo, previewH };
  });
  
  console.log('docH=' + s.docH + ' viewH=' + s.viewH + ' pageScroll=' + s.pageScroll);
  console.log('Buttons:', JSON.stringify(s.btns, null, 2));
  console.log('Chat scroll:', JSON.stringify(s.chatInfo));
  console.log('Preview iframe:', JSON.stringify(s.previewH));
  
  await browser.close();
})();
