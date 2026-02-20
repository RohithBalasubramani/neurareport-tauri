const { chromium } = require('playwright');
const PDF_PATH = '/home/rohith/desktop/NeuraReport/Hyderabad Metropolitan Water Supply & Sewerage Board - Online Bill Payment.pdf';
const BASE = 'http://100.90.185.31:9071';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });

  console.log('[1] Navigate to chat-create page');
  await page.goto(BASE + '/templates/new/chat', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);

  console.log('[2] Upload PDF');
  await page.locator('input[type="file"]').setInputFiles(PDF_PATH);
  await page.waitForTimeout(1000);

  console.log('[3] Send message');
  const ta = page.locator('textarea').first();
  await ta.fill('Create an HMWSSB water bill payment receipt template');
  await ta.press('Enter');

  console.log('[4] Waiting up to 5 min for LLM response...');
  const startTime = Date.now();

  // Poll every 5s to check if the "Processing" placeholder is gone
  // AND we have more than just the user message + welcome message
  let responded = false;
  for (let i = 0; i < 60; i++) { // 60 * 5s = 300s = 5min
    await page.waitForTimeout(5000);
    const elapsed = Math.round((Date.now() - startTime) / 1000);

    const state = await page.evaluate(() => {
      // Check textarea placeholder
      const textareas = document.querySelectorAll('textarea');
      let processing = false;
      for (const t of textareas) {
        if (t.placeholder && t.placeholder.includes('Processing')) processing = true;
      }

      // Count visible chat messages (look for message bubbles)
      const msgs = document.querySelectorAll('[class*="ChatMessage"], [class*="message"]');

      // Check if "Apply Changes" or "Request Different" buttons exist
      const btns = Array.from(document.querySelectorAll('button'))
        .filter(b => ['Apply', 'Request Different'].some(k => b.textContent && b.textContent.includes(k)));

      // Check for any assistant message content (longer text blocks)
      const allText = document.body.innerText;
      const hasAssistantContent = allText.includes('ready_to_apply') ||
                                   allText.includes('Apply Changes') ||
                                   allText.includes('Request Different') ||
                                   allText.length > 2000; // AI response makes page text much longer

      return { processing, msgCount: msgs.length, applyBtns: btns.length, hasAssistantContent, textLen: allText.length };
    });

    console.log(`  [${elapsed}s] processing=${state.processing} msgs=${state.msgCount} applyBtns=${state.applyBtns} textLen=${state.textLen}`);

    if (!state.processing && (state.applyBtns > 0 || (state.hasAssistantContent && state.textLen > 3000))) {
      responded = true;
      console.log(`  LLM responded after ~${elapsed}s`);
      break;
    }
  }

  if (!responded) {
    console.log('  WARNING: LLM may not have responded within 5 min');
  }

  // Wait a bit more for rendering to settle
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/full_e2e_response.png' });
  console.log('[5] Screenshot saved to /tmp/full_e2e_response.png');

  // Detailed layout analysis
  const layout = await page.evaluate(() => {
    const docH = document.documentElement.scrollHeight;
    const viewH = window.innerHeight;

    // All relevant buttons
    const btns = Array.from(document.querySelectorAll('button'))
      .filter(b => ['Apply', 'Request Different', 'Save Template', 'Back', 'Show Preview'].some(k => b.textContent && b.textContent.includes(k)))
      .map(b => {
        const r = b.getBoundingClientRect();
        return { t: b.textContent.trim().substring(0, 40), top: Math.round(r.top), bot: Math.round(r.bottom), inView: r.top >= 0 && r.bottom <= window.innerHeight };
      });

    // Chat scroll container
    let chatInfo = null;
    document.querySelectorAll('*').forEach(el => {
      const cs = window.getComputedStyle(el);
      if ((cs.overflowY === 'auto' || cs.overflow === 'auto') && el.clientHeight > 80) {
        const r = el.getBoundingClientRect();
        if (el.scrollHeight > el.clientHeight + 10 && el.textContent && el.textContent.includes('NeuraReport')) {
          chatInfo = { h: Math.round(r.height), sH: el.scrollHeight, top: Math.round(r.top), bot: Math.round(r.bottom), scrollable: true, scrollTop: Math.round(el.scrollTop) };
        }
      }
    });

    // Preview iframe
    let previewInfo = null;
    const iframes = document.querySelectorAll('iframe');
    if (iframes.length > 0) {
      const r = iframes[0].getBoundingClientRect();
      previewInfo = { h: Math.round(r.height), w: Math.round(r.width), top: Math.round(r.top) };
    }

    // Textarea (chat input)
    let inputInfo = null;
    document.querySelectorAll('textarea').forEach(t => {
      const r = t.getBoundingClientRect();
      inputInfo = { top: Math.round(r.top), bot: Math.round(r.bottom), inView: r.top >= 0 && r.bottom <= window.innerHeight, placeholder: t.placeholder?.substring(0, 50) };
    });

    return { docH, viewH, pageScroll: docH > viewH, btns, chatInfo, previewInfo, inputInfo };
  });

  console.log('\n=== LAYOUT ANALYSIS ===');
  console.log(`Page: docH=${layout.docH} viewH=${layout.viewH} pageScroll=${layout.pageScroll}`);
  console.log('Buttons:', JSON.stringify(layout.btns, null, 2));
  console.log('Chat scroll:', JSON.stringify(layout.chatInfo));
  console.log('Preview iframe:', JSON.stringify(layout.previewInfo));
  console.log('Chat input:', JSON.stringify(layout.inputInfo));

  // If chat is scrollable, scroll to bottom and take another screenshot
  if (layout.chatInfo && layout.chatInfo.scrollable) {
    console.log('\n[6] Scrolling chat to bottom...');
    await page.evaluate(() => {
      document.querySelectorAll('*').forEach(el => {
        const cs = window.getComputedStyle(el);
        if ((cs.overflowY === 'auto' || cs.overflow === 'auto') && el.scrollHeight > el.clientHeight + 50) {
          if (el.textContent?.includes('NeuraReport') && el.getBoundingClientRect().height > 80) {
            el.scrollTop = el.scrollHeight;
          }
        }
      });
    });
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/full_e2e_scrolled.png' });
    console.log('   Scrolled screenshot saved to /tmp/full_e2e_scrolled.png');

    // Re-check button visibility after scroll
    const afterScroll = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button'))
        .filter(b => ['Apply', 'Request Different', 'Save Template', 'Back'].some(k => b.textContent && b.textContent.includes(k)))
        .map(b => {
          const r = b.getBoundingClientRect();
          return { t: b.textContent.trim().substring(0, 40), top: Math.round(r.top), bot: Math.round(r.bottom), inView: r.top >= 0 && r.bottom <= window.innerHeight };
        });
    });
    console.log('Buttons after scroll:', JSON.stringify(afterScroll, null, 2));
  }

  await browser.close();
  console.log('\nDone.');
})();
