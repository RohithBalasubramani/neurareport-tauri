const { chromium } = require('playwright');
const PDF_PATH = '/home/rohith/desktop/NeuraReport/Hyderabad Metropolitan Water Supply & Sewerage Board - Online Bill Payment.pdf';
const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  
  await page.goto(BASE + '/templates/new/chat', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);
  
  await page.locator('input[type="file"]').setInputFiles(PDF_PATH);
  await page.waitForTimeout(1000);
  
  const ta = page.locator('textarea').first();
  await ta.fill('Create an HMWSSB water bill payment receipt');
  await ta.press('Enter');
  
  console.log('Waiting up to 3 min for LLM...');
  
  // Wait for Processing placeholder to go away
  try {
    await page.waitForFunction(() => {
      const textareas = document.querySelectorAll('textarea');
      for (const t of textareas) {
        if (t.placeholder && t.placeholder.includes('Processing')) return false;
      }
      return true;
    }, { timeout: 180000 });
  } catch { console.log('Timeout'); }
  
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/e2e_after_llm.png' });
  
  const s = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'))
      .filter(b => ['Apply','Request Different','Save Template','Back'].some(k => b.textContent && b.textContent.includes(k)))
      .map(b => { const r = b.getBoundingClientRect(); return { t: b.textContent.trim().substring(0,30), top: Math.round(r.top), bot: Math.round(r.bottom), inView: r.top>=0 && r.bottom<=window.innerHeight }; });
    
    let chatInfo = null;
    document.querySelectorAll('*').forEach(el => {
      const cs = window.getComputedStyle(el);
      if ((cs.overflowY === 'auto' || cs.overflow === 'auto') && el.clientHeight > 100 && el.scrollHeight > el.clientHeight + 20) {
        if (el.textContent && el.textContent.includes('NeuraReport')) {
          chatInfo = { h: Math.round(el.clientHeight), sH: el.scrollHeight, scrollable: true };
        }
      }
    });
    
    return { docH: document.documentElement.scrollHeight, viewH: window.innerHeight, btns, chatInfo };
  });
  
  console.log('docH=' + s.docH + ' viewH=' + s.viewH + ' pageScroll=' + (s.docH > s.viewH));
  console.log('Buttons:', JSON.stringify(s.btns));
  console.log('Chat scroll:', JSON.stringify(s.chatInfo));
  
  await browser.close();
  console.log('Done');
})();
