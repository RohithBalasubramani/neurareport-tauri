const { chromium } = require('playwright');

const BASE = 'http://100.90.185.31:9071';
const PDF_PATH = '/home/rohith/desktop/NeuraReport/Hyderabad Metropolitan Water Supply & Sewerage Board - Online Bill Payment.pdf';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  console.log('1. Navigate to chat-create page');
  await page.goto(`${BASE}/templates/new/chat`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/e2e_1_initial.png' });

  // 2. Upload PDF
  console.log('2. Uploading sample PDF...');
  const fileInput = page.locator('input[type="file"][accept="application/pdf"]');
  await fileInput.setInputFiles(PDF_PATH);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/tmp/e2e_2_pdf_uploaded.png' });

  // 3. Type and send message
  console.log('3. Sending message...');
  const textarea = page.locator('textarea').first();
  await textarea.fill('Create an HMWSSB water bill payment receipt');
  await page.waitForTimeout(300);
  await textarea.press('Enter');

  // Wait for AI response
  console.log('   Waiting for AI response (up to 2 min)...');
  try {
    await page.waitForSelector('[role="progressbar"]', { timeout: 10000 }).catch(() => {});
    await page.waitForFunction(() => {
      return document.querySelectorAll('[role="progressbar"]').length === 0;
    }, { timeout: 120000 });
  } catch {
    console.log('   Timeout or no spinner detected');
  }
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/e2e_3_response.png' });

  // 4. Check state
  const state = await page.evaluate(() => {
    const docH = document.documentElement.scrollHeight;
    const viewH = window.innerHeight;

    const btns = Array.from(document.querySelectorAll('button'))
      .filter(b => ['Apply', 'Save', 'Back', 'Request Different'].some(k => b.textContent?.includes(k)))
      .map(b => {
        const r = b.getBoundingClientRect();
        return { text: b.textContent?.trim().substring(0, 40), top: Math.round(r.top), bottom: Math.round(r.bottom), inView: r.top >= 0 && r.bottom <= window.innerHeight };
      });

    // Find the chat scroll container
    let chatScroll = null;
    document.querySelectorAll('*').forEach(el => {
      const s = window.getComputedStyle(el);
      if ((s.overflowY === 'auto' || s.overflow === 'auto') && el.clientHeight > 100) {
        if (el.textContent?.includes('Template Creator') || el.textContent?.includes('NeuraReport')) {
          const r = el.getBoundingClientRect();
          chatScroll = { h: Math.round(r.height), scrollH: el.scrollHeight, canScroll: el.scrollHeight > el.clientHeight + 10 };
        }
      }
    });

    let textarea = null;
    document.querySelectorAll('textarea').forEach(t => {
      const r = t.getBoundingClientRect();
      textarea = { top: Math.round(r.top), bottom: Math.round(r.bottom), inView: r.bottom <= viewH };
    });

    return { docH, viewH, pageScroll: docH > viewH, btns, chatScroll, textarea };
  });

  console.log('\n--- State after AI response ---');
  console.log(`Page: docH=${state.docH} viewH=${state.viewH} scrollable=${state.pageScroll}`);
  console.log('Buttons:', JSON.stringify(state.btns, null, 2));
  console.log('Chat scroll:', state.chatScroll);
  console.log('Textarea:', state.textarea);

  // 5. Scroll chat down and screenshot
  await page.evaluate(() => {
    document.querySelectorAll('*').forEach(el => {
      const s = window.getComputedStyle(el);
      if ((s.overflowY === 'auto' || s.overflow === 'auto') && el.scrollHeight > el.clientHeight + 50) {
        if (el.textContent?.includes('NeuraReport') && el.getBoundingClientRect().height > 100) {
          el.scrollTop = el.scrollHeight;
        }
      }
    });
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/e2e_4_scrolled.png' });

  const afterScroll = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button'))
      .filter(b => ['Apply', 'Save', 'Back', 'Request Different'].some(k => b.textContent?.includes(k)))
      .map(b => {
        const r = b.getBoundingClientRect();
        return { text: b.textContent?.trim().substring(0, 40), top: Math.round(r.top), bottom: Math.round(r.bottom), inView: r.top >= 0 && r.bottom <= window.innerHeight };
      });
  });
  console.log('\nButtons after scroll:', JSON.stringify(afterScroll, null, 2));

  await browser.close();
  console.log('\nDone.');
})();
