const { chromium } = require('playwright');

const BASE = 'http://127.0.0.1:5180/neurareport';
const SCREENSHOT_DIR = '/home/rohith/desktop/NeuraReport/screenshots';

const PAGES = [
  { name: '01-dashboard',          path: '/' },
  { name: '02-dashboard-alt',      path: '/dashboard' },
  { name: '03-connections',        path: '/connections' },
  { name: '04-templates',          path: '/templates' },
  { name: '05-templates-new-chat', path: '/templates/new/chat' },
  { name: '06-jobs',               path: '/jobs' },
  { name: '07-reports',            path: '/reports' },
  { name: '08-schedules',          path: '/schedules' },
  { name: '09-analyze',            path: '/analyze' },
  { name: '10-analyze-legacy',     path: '/analyze/legacy' },
  { name: '11-settings',           path: '/settings' },
  { name: '12-activity',           path: '/activity' },
  { name: '13-history',            path: '/history' },
  { name: '14-stats',              path: '/stats' },
  { name: '15-ops',                path: '/ops' },
  { name: '16-query',              path: '/query' },
  { name: '17-enrichment',         path: '/enrichment' },
  { name: '18-federation',         path: '/federation' },
  { name: '19-synthesis',          path: '/synthesis' },
  { name: '20-docqa',              path: '/docqa' },
  { name: '21-summary',            path: '/summary' },
  { name: '22-documents',          path: '/documents' },
  { name: '23-spreadsheets',       path: '/spreadsheets' },
  { name: '24-dashboard-builder',  path: '/dashboard-builder' },
  { name: '25-connectors',         path: '/connectors' },
  { name: '26-workflows',          path: '/workflows' },
  { name: '27-agents',             path: '/agents' },
  { name: '28-search',             path: '/search' },
  { name: '29-visualization',      path: '/visualization' },
  { name: '30-knowledge',          path: '/knowledge' },
  { name: '31-design',             path: '/design' },
  { name: '32-ingestion',          path: '/ingestion' },
  { name: '33-widgets',            path: '/widgets' },
  { name: '34-setup-wizard',       path: '/setup/wizard' },
  { name: '35-not-found',          path: '/nonexistent-page' },
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  // Suppress console noise
  page.on('console', () => {});
  page.on('pageerror', () => {});

  console.log(`Capturing ${PAGES.length} pages...\n`);

  for (const { name, path } of PAGES) {
    const url = `${BASE}${path}`;
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
      // Wait a bit for React to settle and animations to complete
      await page.waitForTimeout(1500);
      const filepath = `${SCREENSHOT_DIR}/${name}.png`;
      await page.screenshot({ path: filepath, fullPage: false });
      console.log(`OK  ${name}  (${path})`);
    } catch (err) {
      // Still try to take a screenshot even on timeout
      try {
        const filepath = `${SCREENSHOT_DIR}/${name}.png`;
        await page.screenshot({ path: filepath, fullPage: false });
        console.log(`WARN  ${name}  (${path}) - ${err.message.split('\n')[0]}`);
      } catch {
        console.log(`FAIL  ${name}  (${path}) - ${err.message.split('\n')[0]}`);
      }
    }
  }

  await browser.close();
  console.log(`\nDone. Screenshots saved to ${SCREENSHOT_DIR}/`);
})();
