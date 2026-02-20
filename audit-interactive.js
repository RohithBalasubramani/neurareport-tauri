const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE = 'http://127.0.0.1:5180/neurareport';
const DIR = '/home/rohith/desktop/NeuraReport/audit-screenshots';

// Ensure output directory
fs.mkdirSync(DIR, { recursive: true });

let shotIndex = 0;

async function snap(page, label) {
  shotIndex++;
  const num = String(shotIndex).padStart(3, '0');
  const safeName = label.replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 80);
  const filepath = path.join(DIR, `${num}-${safeName}.png`);
  await page.screenshot({ path: filepath, fullPage: false });
  console.log(`  [${num}] ${label}`);
}

async function snapFull(page, label) {
  shotIndex++;
  const num = String(shotIndex).padStart(3, '0');
  const safeName = label.replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 80);
  const filepath = path.join(DIR, `${num}-${safeName}.png`);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`  [${num}] ${label} (fullpage)`);
}

async function hover(page, selector, label) {
  try {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2000 })) {
      await el.hover();
      await page.waitForTimeout(400);
      await snap(page, label);
    }
  } catch {}
}

async function clickAndSnap(page, selector, label, waitMs = 1000) {
  try {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2000 })) {
      await el.click();
      await page.waitForTimeout(waitMs);
      await snap(page, label);
      return true;
    }
  } catch {}
  return false;
}

async function focusAndSnap(page, selector, label) {
  try {
    const el = page.locator(selector).first();
    if (await el.isVisible({ timeout: 2000 })) {
      await el.focus();
      await page.waitForTimeout(300);
      await snap(page, label);
    }
  } catch {}
}

async function scrollAndSnap(page, label) {
  // Scroll to bottom of main content
  try {
    await page.evaluate(() => {
      const main = document.querySelector('main') || document.querySelector('[class*="content"]') || document.documentElement;
      main.scrollTo(0, main.scrollHeight);
    });
    await page.waitForTimeout(500);
    await snap(page, label);
  } catch {}
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  page.on('console', () => {});
  page.on('pageerror', () => {});

  const go = async (url) => {
    try {
      await page.goto(`${BASE}${url}`, { waitUntil: 'networkidle', timeout: 15000 });
    } catch {
      // Still continue on timeout
    }
    await page.waitForTimeout(1500);
  };

  // ========================================================================
  // 1. DASHBOARD
  // ========================================================================
  console.log('\n=== DASHBOARD ===');
  await go('/');
  await snap(page, 'dashboard-default');
  await snapFull(page, 'dashboard-default-fullpage');

  // Test sidebar hover states
  await hover(page, 'text=Dashboard', 'sidebar-dashboard-hover');
  await hover(page, 'text=My Reports', 'sidebar-myreports-hover');
  await hover(page, 'text=Templates', 'sidebar-templates-hover');
  await hover(page, 'text=Data Sources', 'sidebar-datasources-hover');

  // Test top nav elements
  await hover(page, '[data-testid="notifications-button"], [aria-label*="notification" i]', 'topnav-bell-hover');
  await hover(page, '[aria-label*="help" i], [data-testid="help-button"]', 'topnav-help-hover');
  await hover(page, '[aria-label*="shortcut" i], [data-testid="keyboard-shortcuts-button"]', 'topnav-shortcuts-hover');

  // Click search bar
  await focusAndSnap(page, 'input[placeholder*="Search" i]', 'topnav-search-focus');

  // Try "+ New Report" button
  await hover(page, 'text=New Report', 'sidebar-newreport-hover');
  await clickAndSnap(page, 'text=New Report', 'sidebar-newreport-click');

  // Quick Actions
  await go('/');
  await page.waitForTimeout(500);
  await hover(page, 'text=Manage Connections', 'dashboard-quickaction-connections-hover');
  await hover(page, 'text=Report Designs', 'dashboard-quickaction-designs-hover');

  // AI Recommendations
  await hover(page, '[class*="recommendation" i], [class*="Recommendation"]', 'dashboard-ai-recommendations-hover');

  // Scroll dashboard
  await scrollAndSnap(page, 'dashboard-scrolled-bottom');

  // ========================================================================
  // 2. CONNECTIONS / DATA SOURCES
  // ========================================================================
  console.log('\n=== CONNECTIONS ===');
  await go('/connections');
  await snap(page, 'connections-default');
  await snapFull(page, 'connections-fullpage');

  // Hover table rows
  await hover(page, 'tr:has-text("HMWSSB")', 'connections-hmwssb-row-hover');
  await hover(page, 'tr:has-text("Fixture 01")', 'connections-fixture01-row-hover');

  // Click "+ Add Data Source" button
  await clickAndSnap(page, 'text=Add Data Source', 'connections-add-datasource-click', 1500);
  // Close any dialog that opened
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Hover filter button
  await hover(page, 'text=Filters', 'connections-filters-hover');
  await clickAndSnap(page, 'text=Filters', 'connections-filters-open', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Focus search input
  await focusAndSnap(page, 'input[placeholder*="Search connections" i]', 'connections-search-focus');

  // Click kebab menu on a row
  await clickAndSnap(page, 'tr:has-text("HMWSSB") button[aria-label*="more" i], tr:has-text("HMWSSB") [class*="kebab"], tr:has-text("HMWSSB") svg:last-of-type', 'connections-hmwssb-kebab-click', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Star/favorite a connection
  await hover(page, 'tr:has-text("Fixture 01") [aria-label*="star" i], tr:has-text("Fixture 01") [aria-label*="favorite" i]', 'connections-star-hover');

  // ========================================================================
  // 3. TEMPLATES
  // ========================================================================
  console.log('\n=== TEMPLATES ===');
  await go('/templates');
  await snap(page, 'templates-default');
  await snapFull(page, 'templates-fullpage');

  // Hover action buttons
  await hover(page, 'text=Create with AI', 'templates-createai-hover');
  await hover(page, 'text=Upload Design', 'templates-upload-hover');
  await hover(page, 'text=Import Backup', 'templates-import-hover');

  // Hover table rows
  await hover(page, 'tr:has-text("HMWSSB Bill Payment")', 'templates-hmwssb-row-hover');
  await hover(page, 'tr:has-text("CrystalReport")', 'templates-crystal-row-hover');

  // Click a template row to see detail
  await clickAndSnap(page, 'td:has-text("HMWSSB Bill Payment")', 'templates-hmwssb-detail-click', 1500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Check checkbox hover
  await hover(page, 'tr:has-text("01_online") input[type="checkbox"], tr:has-text("01_online") [class*="Checkbox"]', 'templates-checkbox-hover');

  // ========================================================================
  // 4. TEMPLATES - NEW CHAT (Create with AI)
  // ========================================================================
  console.log('\n=== TEMPLATES - CREATE WITH AI ===');
  await go('/templates/new/chat');
  await snap(page, 'templates-chat-default');

  // Focus chat input
  await focusAndSnap(page, 'input[placeholder*="Describe" i], textarea[placeholder*="Describe" i]', 'templates-chat-input-focus');

  // Hover Save/Back buttons
  await hover(page, 'text=Save Template', 'templates-chat-save-hover');
  await hover(page, 'text=Back', 'templates-chat-back-hover');

  // Hover PDF upload area
  await hover(page, 'text=Have a sample PDF', 'templates-chat-pdf-upload-hover');

  // ========================================================================
  // 5. JOBS
  // ========================================================================
  console.log('\n=== JOBS ===');
  await go('/jobs');
  await snap(page, 'jobs-default');
  await snapFull(page, 'jobs-fullpage');

  // Hover Refresh button
  await hover(page, 'text=Refresh', 'jobs-refresh-hover');

  // Hover different status rows
  await hover(page, 'tr:has-text("Completed"):first-of-type', 'jobs-completed-row-hover');
  await hover(page, 'tr:has-text("Failed"):first-of-type', 'jobs-failed-row-hover');

  // ========================================================================
  // 6. REPORTS (My Reports)
  // ========================================================================
  console.log('\n=== REPORTS ===');
  await go('/reports');
  await snap(page, 'reports-default');
  await snapFull(page, 'reports-fullpage');

  // Click time period buttons
  await clickAndSnap(page, 'text=Today', 'reports-period-today');
  await clickAndSnap(page, 'text=This Week', 'reports-period-thisweek');
  await clickAndSnap(page, 'text=Last Month', 'reports-period-lastmonth');
  await clickAndSnap(page, 'text=This Month', 'reports-period-thismonth');

  // Hover recent run action buttons
  await hover(page, 'button:has-text("PDF"):near(:text("HMWSSB Bill Payment"))', 'reports-pdf-download-hover');
  await hover(page, 'button:has-text("HTML"):near(:text("HMWSSB Bill Payment"))', 'reports-html-download-hover');
  await hover(page, 'button:has-text("Analyze"):near(:text("HMWSSB Bill Payment"))', 'reports-analyze-hover');

  // Hover "View Progress" link
  await hover(page, 'text=View Progress', 'reports-view-progress-hover');

  // AI Template Picker accordion
  await clickAndSnap(page, 'text=AI Template Picker', 'reports-ai-picker-expand', 800);

  // ========================================================================
  // 7. SCHEDULES
  // ========================================================================
  console.log('\n=== SCHEDULES ===');
  await go('/schedules');
  await snap(page, 'schedules-default');

  // Hover Create Schedule button
  await hover(page, 'text=Create Schedule', 'schedules-create-hover');
  await clickAndSnap(page, 'text=Create Schedule', 'schedules-create-click', 1500);
  await snap(page, 'schedules-create-dialog');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Hover toggle switch
  await hover(page, '[role="checkbox"], [class*="Switch"]', 'schedules-toggle-hover');

  // ========================================================================
  // 8. ANALYZE
  // ========================================================================
  console.log('\n=== ANALYZE ===');
  await go('/analyze');
  await snap(page, 'analyze-default');
  await snapFull(page, 'analyze-fullpage');

  // Hover upload zone
  await hover(page, 'text=Drop your document here', 'analyze-dropzone-hover');

  // Hover format chips
  await hover(page, 'text=PDF', 'analyze-pdf-chip-hover');
  await hover(page, 'text=Excel', 'analyze-excel-chip-hover');

  // ========================================================================
  // 9. ANALYZE LEGACY
  // ========================================================================
  console.log('\n=== ANALYZE LEGACY ===');
  await go('/analyze/legacy');
  await snap(page, 'analyze-legacy-default');

  // Hover drop zone
  await hover(page, 'text=Drop a document here', 'analyze-legacy-dropzone-hover');

  // ========================================================================
  // 10. SETTINGS
  // ========================================================================
  console.log('\n=== SETTINGS ===');
  await go('/settings');
  await snap(page, 'settings-default');
  await snapFull(page, 'settings-fullpage');

  // Focus language dropdown
  await clickAndSnap(page, '[class*="Select"]:near(:text("Language")), [aria-label*="Language" i]', 'settings-language-dropdown', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Hover Change Password button
  await hover(page, 'text=Change Password >> button', 'settings-change-password-hover');

  // Hover 2FA toggle
  await hover(page, ':text("Two-Factor") ~ [role="checkbox"], :text("Two-Factor") ~ [class*="Switch"]', 'settings-2fa-toggle-hover');

  // Scroll to see System Status
  await scrollAndSnap(page, 'settings-scrolled-systemstatus');

  // ========================================================================
  // 11. ACTIVITY
  // ========================================================================
  console.log('\n=== ACTIVITY ===');
  await go('/activity');
  await snap(page, 'activity-default');

  // Hover refresh button
  await hover(page, '[aria-label*="refresh" i], button:has(svg):near(:text("Activity Log"))', 'activity-refresh-hover');

  // Click Entity Type filter
  await clickAndSnap(page, 'text=Entity Type', 'activity-entitytype-dropdown', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Click Action filter
  await clickAndSnap(page, ':text("Action") >> .. >> [role="combobox"], :text("Action"):not(:text("Quick"))', 'activity-action-dropdown', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // ========================================================================
  // 12. HISTORY
  // ========================================================================
  console.log('\n=== HISTORY ===');
  await go('/history');
  await snap(page, 'history-default');
  await snapFull(page, 'history-fullpage');

  // Hover Generate New button
  await hover(page, 'text=Generate New', 'history-generate-hover');

  // Hover table rows
  await hover(page, 'tr:has-text("HMWSSB Bill Payment"):first-of-type', 'history-hmwssb-row-hover');

  // Click Status filter
  await clickAndSnap(page, '[class*="Select"]:near(:text("Status")), :text("Status") >> .. >> [role="combobox"]', 'history-status-filter', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // ========================================================================
  // 13. STATS
  // ========================================================================
  console.log('\n=== STATS ===');
  await go('/stats');
  await snap(page, 'stats-default');
  await snapFull(page, 'stats-fullpage');

  // Click tab buttons
  await clickAndSnap(page, 'text=Jobs', 'stats-jobs-tab', 1000);
  await clickAndSnap(page, 'text=Templates', 'stats-templates-tab', 1000);
  await clickAndSnap(page, 'text=Overview', 'stats-overview-tab', 1000);

  // Hover stat cards
  await hover(page, ':text("TOTAL JOBS") >> ..', 'stats-totaljobs-card-hover');
  await hover(page, ':text("SUCCESS RATE") >> ..', 'stats-successrate-card-hover');

  // Hover Export button
  await hover(page, 'text=Export', 'stats-export-hover');

  // Time period dropdown
  await clickAndSnap(page, ':text("Last 7 days") >> ..', 'stats-timeperiod-dropdown', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // ========================================================================
  // 14. OPS
  // ========================================================================
  console.log('\n=== OPS ===');
  await go('/ops');
  await snap(page, 'ops-default');
  await snapFull(page, 'ops-fullpage');

  // Focus input fields
  await focusAndSnap(page, 'input[placeholder*="X-API-Key" i]', 'ops-apikey-focus');
  await focusAndSnap(page, 'input[placeholder*="Bearer" i]', 'ops-bearer-focus');
  await focusAndSnap(page, 'input[placeholder*="Email" i]:first-of-type', 'ops-register-email-focus');

  // Hover action buttons
  await hover(page, 'text=Register User', 'ops-register-hover');
  await hover(page, 'text=Get Access Token', 'ops-gettoken-hover');
  await hover(page, 'text=List Users', 'ops-listusers-hover');

  // Scroll to health section
  await scrollAndSnap(page, 'ops-health-section');

  // ========================================================================
  // 15. QUERY
  // ========================================================================
  console.log('\n=== QUERY ===');
  await go('/query');
  await snap(page, 'query-default');

  // Focus query input
  await focusAndSnap(page, 'textarea, input[placeholder*="question" i]', 'query-input-focus');

  // Hover Generate SQL
  await hover(page, 'text=Generate SQL', 'query-generate-hover');

  // Hover Saved/History buttons
  await hover(page, 'text=Saved', 'query-saved-hover');
  await hover(page, ':text("History"):near(:text("Saved"))', 'query-history-hover');

  // ========================================================================
  // 16. ENRICHMENT
  // ========================================================================
  console.log('\n=== ENRICHMENT ===');
  await go('/enrichment');
  await snap(page, 'enrichment-default');
  await snapFull(page, 'enrichment-fullpage');

  // Hover enrichment source cards
  await hover(page, 'text=Company Information', 'enrichment-company-hover');
  await hover(page, 'text=Address Standardization', 'enrichment-address-hover');
  await hover(page, 'text=Currency Exchange', 'enrichment-currency-hover');

  // Click Cache Admin tab
  await clickAndSnap(page, 'text=Cache Admin', 'enrichment-cacheadmin-tab', 1000);

  // Go back to Enrich Data
  await clickAndSnap(page, 'text=Enrich Data', 'enrichment-enrichdata-tab', 800);

  // Hover disabled buttons
  await hover(page, 'text=Preview', 'enrichment-preview-disabled-hover');
  await hover(page, 'text=Enrich All', 'enrichment-enrichall-disabled-hover');

  // ========================================================================
  // 17. FEDERATION
  // ========================================================================
  console.log('\n=== FEDERATION ===');
  await go('/federation');
  await snap(page, 'federation-default');

  // Hover New Virtual Schema button
  await hover(page, 'text=New Virtual Schema', 'federation-newschema-hover');

  // ========================================================================
  // 18. SYNTHESIS
  // ========================================================================
  console.log('\n=== SYNTHESIS ===');
  await go('/synthesis');
  await snap(page, 'synthesis-default');

  // Hover New Session button
  await hover(page, 'text=New Session', 'synthesis-newsession-hover');

  // ========================================================================
  // 19. DOCQA
  // ========================================================================
  console.log('\n=== DOCQA ===');
  await go('/docqa');
  await snap(page, 'docqa-default');

  // Click existing session
  await clickAndSnap(page, 'text=sxsa', 'docqa-session-click', 1500);

  // Hover Create Your First Session CTA
  await hover(page, 'text=Create Your First Session', 'docqa-create-cta-hover');

  // Hover New Session button
  await hover(page, ':text("New Session"):near(:text("Document Q&A"))', 'docqa-newsession-hover');

  // ========================================================================
  // 20. SUMMARY
  // ========================================================================
  console.log('\n=== SUMMARY ===');
  await go('/summary');
  await snap(page, 'summary-default');
  await snapFull(page, 'summary-fullpage');

  // Focus text area
  await focusAndSnap(page, 'textarea[placeholder*="Paste" i]', 'summary-textarea-focus');

  // Hover Tone dropdown
  await clickAndSnap(page, ':text("Formal") >> ..', 'summary-tone-dropdown', 800);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // ========================================================================
  // 21. DOCUMENTS
  // ========================================================================
  console.log('\n=== DOCUMENTS ===');
  await go('/documents');
  await snap(page, 'documents-default');

  // Hover New Document button
  await hover(page, 'text=New Document', 'documents-newdoc-hover');

  // Hover Create Document CTA
  await hover(page, 'text=Create Document', 'documents-create-cta-hover');

  // ========================================================================
  // 22. SPREADSHEETS
  // ========================================================================
  console.log('\n=== SPREADSHEETS ===');
  await go('/spreadsheets');
  await snap(page, 'spreadsheets-default');

  // Hover buttons
  await hover(page, 'text=Create Spreadsheet', 'spreadsheets-create-hover');
  await hover(page, 'text=Import File', 'spreadsheets-import-hover');

  // ========================================================================
  // 23. DASHBOARD BUILDER
  // ========================================================================
  console.log('\n=== DASHBOARD BUILDER ===');
  await go('/dashboard-builder');
  await snap(page, 'dashbuilder-default');

  // Hover Create Dashboard
  await hover(page, 'text=Create Dashboard', 'dashbuilder-create-hover');

  // ========================================================================
  // 24. CONNECTORS
  // ========================================================================
  console.log('\n=== CONNECTORS ===');
  await go('/connectors');
  await snap(page, 'connectors-default');
  await snapFull(page, 'connectors-fullpage');

  // Hover connector cards
  await hover(page, 'text=PostgreSQL >> ..', 'connectors-postgres-hover');
  await hover(page, 'text=MySQL >> ..', 'connectors-mysql-hover');
  await hover(page, 'text=MongoDB >> ..', 'connectors-mongodb-hover');

  // Click a Connect button
  await hover(page, 'button:has-text("Connect"):near(:text("PostgreSQL"))', 'connectors-postgres-connect-hover');
  await clickAndSnap(page, 'button:has-text("Connect"):near(:text("PostgreSQL"))', 'connectors-postgres-connect-click', 1500);
  await snap(page, 'connectors-postgres-dialog');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Switch to My Connections tab
  await clickAndSnap(page, 'text=My Connections', 'connectors-myconnections-tab', 1000);

  // Scroll to Cloud Storage
  await go('/connectors');
  await page.waitForTimeout(500);
  await scrollAndSnap(page, 'connectors-cloud-storage-section');

  // Hover cloud storage cards
  await hover(page, 'text=Google Drive >> ..', 'connectors-gdrive-hover');
  await hover(page, 'text=Amazon S3 >> ..', 'connectors-s3-hover');

  // ========================================================================
  // 25. WORKFLOWS
  // ========================================================================
  console.log('\n=== WORKFLOWS ===');
  await go('/workflows');
  await snap(page, 'workflows-default');

  // Hover buttons
  await hover(page, 'text=New Workflow', 'workflows-new-hover');
  await hover(page, 'text=Create Workflow', 'workflows-create-cta-hover');

  // ========================================================================
  // 26. AGENTS
  // ========================================================================
  console.log('\n=== AGENTS ===');
  await go('/agents');
  await snap(page, 'agents-default');
  await snapFull(page, 'agents-fullpage');

  // Hover agent cards
  await hover(page, 'text=Research Agent >> ..', 'agents-research-hover');
  await hover(page, 'text=Data Analyst >> ..', 'agents-dataanalyst-hover');
  await hover(page, 'text=Email Draft >> ..', 'agents-emaildraft-hover');
  await hover(page, 'text=Content Repurpose >> ..', 'agents-content-hover');
  await hover(page, 'text=Proofreading >> ..', 'agents-proofread-hover');
  await hover(page, 'text=Report Analyst >> ..', 'agents-reportanalyst-hover');

  // Click Data Analyst card
  await clickAndSnap(page, ':text("Data Analyst") >> ..', 'agents-dataanalyst-selected', 1000);

  // Click History button
  await clickAndSnap(page, 'text=History', 'agents-history-click', 1500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Focus Research Topic textarea
  await go('/agents');
  await page.waitForTimeout(800);
  await focusAndSnap(page, 'textarea[placeholder*="Research" i], textarea', 'agents-research-input-focus');

  // Hover Run button (likely disabled)
  await hover(page, 'text=Run Research Agent', 'agents-run-hover');

  // ========================================================================
  // 27. SEARCH
  // ========================================================================
  console.log('\n=== SEARCH ===');
  await go('/search');
  await snap(page, 'search-default');

  // Focus search input
  await focusAndSnap(page, 'input[placeholder*="Search documents" i]', 'search-input-focus');

  // Click search tabs
  await clickAndSnap(page, 'text=Semantic', 'search-semantic-tab', 800);
  await clickAndSnap(page, 'text=Regex', 'search-regex-tab', 800);
  await clickAndSnap(page, 'text=Boolean', 'search-boolean-tab', 800);
  await clickAndSnap(page, 'text=Full Text', 'search-fulltext-tab', 800);

  // Hover example searches
  await hover(page, 'text=quarterly revenue', 'search-example-fulltext-hover');
  await hover(page, 'text=documents about marketing', 'search-example-semantic-hover');

  // Hover Search button
  await hover(page, 'button:has-text("Search")', 'search-button-hover');

  // ========================================================================
  // 28. VISUALIZATION
  // ========================================================================
  console.log('\n=== VISUALIZATION ===');
  await go('/visualization');
  await snap(page, 'visualization-default');
  await snapFull(page, 'visualization-fullpage');

  // Click different diagram types
  await clickAndSnap(page, 'text=Mind Map', 'visualization-mindmap-selected', 800);
  await clickAndSnap(page, 'text=Gantt Chart', 'visualization-gantt-selected', 800);
  await clickAndSnap(page, 'text=Kanban Board', 'visualization-kanban-selected', 800);
  await clickAndSnap(page, 'text=Flowchart', 'visualization-flowchart-selected', 800);

  // Hover Upload button
  await hover(page, 'text=Upload Excel', 'visualization-upload-hover');

  // ========================================================================
  // 29. KNOWLEDGE
  // ========================================================================
  console.log('\n=== KNOWLEDGE ===');
  await go('/knowledge');
  await snap(page, 'knowledge-default');
  await snapFull(page, 'knowledge-fullpage');

  // Hover document cards
  await hover(page, 'text=Security Compliance Checklist >> ..', 'knowledge-security-card-hover');
  await hover(page, 'text=Competitor Analysis Report >> ..', 'knowledge-competitor-card-hover');

  // Click collection items
  await clickAndSnap(page, 'text=Marketing Assets', 'knowledge-marketing-collection', 1000);
  await clickAndSnap(page, 'text=All Documents', 'knowledge-alldocs', 800);

  // Hover action buttons
  await hover(page, 'text=Upload Document', 'knowledge-upload-hover');
  await hover(page, 'text=Knowledge Graph', 'knowledge-graph-hover');
  await hover(page, 'text=Generate FAQ', 'knowledge-faq-hover');

  // Focus search
  await focusAndSnap(page, 'input[placeholder*="Search" i]:near(:text("All Documents"))', 'knowledge-search-focus');

  // Click Favorites
  await clickAndSnap(page, 'text=Favorites', 'knowledge-favorites', 1000);

  // Click Knowledge Graph nav
  await clickAndSnap(page, ':text("Knowledge Graph"):near(:text("Favorites"))', 'knowledge-graph-nav', 1000);

  // ========================================================================
  // 30. DESIGN (Brand Kit)
  // ========================================================================
  console.log('\n=== DESIGN (BRAND KIT) ===');
  await go('/design');
  await snap(page, 'design-default');

  // Click tabs
  await clickAndSnap(page, 'text=Themes', 'design-themes-tab', 1000);
  await snap(page, 'design-themes-content');
  await clickAndSnap(page, 'text=Color Tools', 'design-colortools-tab', 1000);
  await snap(page, 'design-colortools-content');
  await clickAndSnap(page, 'text=Typography', 'design-typography-tab', 1000);
  await snap(page, 'design-typography-content');
  await clickAndSnap(page, 'text=Brand Kits', 'design-brandkits-tab', 800);

  // Hover brand kit cards
  await hover(page, 'text=Professional Dark >> ..', 'design-profdark-hover');
  await hover(page, 'text=Modern Green >> ..', 'design-modgreen-hover');

  // Hover action buttons on a card
  await hover(page, 'text=Set Default >> ..:near(:text("Professional Dark"))', 'design-setdefault-hover');

  // Click New Brand Kit
  await hover(page, 'text=New Brand Kit', 'design-newbrandkit-hover');
  await clickAndSnap(page, 'text=New Brand Kit', 'design-newbrandkit-click', 1500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // ========================================================================
  // 31. INGESTION
  // ========================================================================
  console.log('\n=== INGESTION ===');
  await go('/ingestion');
  await snap(page, 'ingestion-default');

  // Click different import methods
  await clickAndSnap(page, 'text=URL Import', 'ingestion-urlimport', 800);
  await clickAndSnap(page, 'text=Web Clipper', 'ingestion-webclipper', 800);
  await clickAndSnap(page, 'text=Folder Watcher', 'ingestion-folderwatcher', 800);
  await clickAndSnap(page, 'text=Email Import', 'ingestion-emailimport', 800);
  await clickAndSnap(page, 'text=Transcription', 'ingestion-transcription', 800);
  await clickAndSnap(page, 'text=Database Import', 'ingestion-dbimport', 800);
  await clickAndSnap(page, 'text=File Upload', 'ingestion-fileupload', 800);

  // Hover drop zone
  await hover(page, 'text=Drag & drop files here', 'ingestion-dropzone-hover');

  // ========================================================================
  // 32. WIDGETS
  // ========================================================================
  console.log('\n=== WIDGETS ===');
  await go('/widgets');
  await snap(page, 'widgets-default');

  // ========================================================================
  // 33. SETUP WIZARD
  // ========================================================================
  console.log('\n=== SETUP WIZARD ===');
  await go('/setup/wizard');
  await snap(page, 'wizard-default');
  await snapFull(page, 'wizard-fullpage');

  // Hover Quick Start cards
  await hover(page, 'text=Try Demo Mode >> ..', 'wizard-demo-hover');
  await hover(page, 'text=Skip for Now >> ..', 'wizard-skip-hover');

  // Click data source radio
  await clickAndSnap(page, 'text=Fixture 01', 'wizard-fixture01-select', 800);

  // ========================================================================
  // 34. 404 NOT FOUND
  // ========================================================================
  console.log('\n=== 404 ===');
  await go('/nonexistent-page');
  await snap(page, '404-default');

  // Hover buttons
  await hover(page, 'text=Go Back', '404-goback-hover');
  await hover(page, 'text=Go to Dashboard', '404-godashboard-hover');

  // ========================================================================
  // CROSS-PAGE TESTS: TopNav interactions
  // ========================================================================
  console.log('\n=== TOPNAV INTERACTION TESTS ===');
  await go('/connections');

  // Click keyboard shortcuts button
  await clickAndSnap(page, '[aria-label*="shortcut" i], [data-testid="keyboard-shortcuts-button"]', 'topnav-shortcuts-dialog', 1500);
  await snap(page, 'topnav-shortcuts-dialog-content');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Click help button
  await clickAndSnap(page, '[aria-label*="help" i], [data-testid="help-button"]', 'topnav-help-panel', 1500);
  await snap(page, 'topnav-help-panel-content');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Click user avatar/profile
  await clickAndSnap(page, '[data-testid="user-menu"], [aria-label*="user" i], [aria-label*="profile" i], [aria-label*="account" i]', 'topnav-user-menu', 1500);
  await snap(page, 'topnav-user-menu-content');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Click jobs/notifications badge
  await clickAndSnap(page, '[data-testid="notifications-button"], [aria-label*="notification" i]:not([aria-label*="bell"]):last-of-type', 'topnav-jobs-panel', 1500);
  await snap(page, 'topnav-jobs-panel-content');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Click connection indicator chip
  await clickAndSnap(page, 'text=HMWSSB Billing DB', 'topnav-connection-chip-click', 1000);
  await snap(page, 'topnav-connection-dropdown');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Global search: type something
  await go('/connections');
  await page.waitForTimeout(500);
  const searchInput = page.locator('input[placeholder*="Search..." i]').first();
  if (await searchInput.isVisible({ timeout: 2000 })) {
    await searchInput.fill('test');
    await page.waitForTimeout(1000);
    await snap(page, 'topnav-search-results-test');
    await searchInput.fill('');
    await page.waitForTimeout(500);
  }

  // ========================================================================
  // SIDEBAR: Collapse/Expand test
  // ========================================================================
  console.log('\n=== SIDEBAR TESTS ===');
  await go('/connections');
  await snap(page, 'sidebar-expanded');

  // Look for sidebar collapse toggle
  await clickAndSnap(page, '[aria-label*="collapse" i], [aria-label*="toggle" i]:near(:text("NeuraReport")), [class*="collapse" i]', 'sidebar-collapsed', 1000);
  await snap(page, 'sidebar-collapsed-state');

  // Try to re-expand
  await clickAndSnap(page, '[aria-label*="expand" i], [aria-label*="toggle" i], [class*="expand" i]', 'sidebar-reexpanded', 1000);

  // ========================================================================
  // DIALOG / MODAL TESTS
  // ========================================================================
  console.log('\n=== DIALOG TESTS ===');

  // Connections: Add Data Source dialog
  await go('/connections');
  await clickAndSnap(page, 'text=Add Data Source', 'dialog-add-datasource', 1500);
  await snapFull(page, 'dialog-add-datasource-fullpage');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Templates: try clicking a template for detail view
  await go('/templates');
  await page.waitForTimeout(800);
  // Click first template name
  await clickAndSnap(page, 'td:has-text("01_onlineinvoices")', 'dialog-template-detail', 1500);
  await snap(page, 'dialog-template-detail-content');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // Schedules: Create Schedule dialog
  await go('/schedules');
  await clickAndSnap(page, 'text=Create Schedule', 'dialog-create-schedule', 1500);
  await snapFull(page, 'dialog-create-schedule-fullpage');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // ========================================================================
  // RESPONSIVE: Test narrower viewport
  // ========================================================================
  console.log('\n=== RESPONSIVE TESTS ===');

  // 1024px width
  await page.setViewportSize({ width: 1024, height: 768 });
  await go('/');
  await snap(page, 'responsive-1024-dashboard');
  await go('/connections');
  await snap(page, 'responsive-1024-connections');
  await go('/templates');
  await snap(page, 'responsive-1024-templates');
  await go('/connectors');
  await snap(page, 'responsive-1024-connectors');
  await go('/knowledge');
  await snap(page, 'responsive-1024-knowledge');
  await go('/agents');
  await snap(page, 'responsive-1024-agents');

  // 768px (tablet)
  await page.setViewportSize({ width: 768, height: 1024 });
  await go('/');
  await snap(page, 'responsive-768-dashboard');
  await go('/connections');
  await snap(page, 'responsive-768-connections');
  await go('/templates');
  await snap(page, 'responsive-768-templates');
  await go('/connectors');
  await snap(page, 'responsive-768-connectors');
  await go('/knowledge');
  await snap(page, 'responsive-768-knowledge');
  await go('/agents');
  await snap(page, 'responsive-768-agents');
  await go('/reports');
  await snap(page, 'responsive-768-reports');

  // Reset viewport
  await page.setViewportSize({ width: 1440, height: 900 });

  // ========================================================================
  // CSS COMPUTED STYLES EXTRACTION
  // ========================================================================
  console.log('\n=== EXTRACTING CSS METRICS ===');
  await go('/connections');
  await page.waitForTimeout(800);

  const metrics = await page.evaluate(() => {
    const result = {};
    const getComputed = (el) => {
      if (!el) return null;
      const s = getComputedStyle(el);
      return {
        fontFamily: s.fontFamily,
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        lineHeight: s.lineHeight,
        letterSpacing: s.letterSpacing,
        color: s.color,
        backgroundColor: s.backgroundColor,
        borderColor: s.borderColor,
        borderRadius: s.borderRadius,
        padding: s.padding,
        margin: s.margin,
        boxShadow: s.boxShadow,
        gap: s.gap,
      };
    };

    // Sidebar
    const sidebar = document.querySelector('nav, [class*="sidebar" i], [class*="Sidebar" i]');
    result.sidebar = getComputed(sidebar);
    if (sidebar) result.sidebarWidth = sidebar.getBoundingClientRect().width;

    // Sidebar items
    const sidebarItem = document.querySelector('nav a, [class*="sidebar" i] a, [class*="NavItem" i]');
    result.sidebarItem = getComputed(sidebarItem);

    // Top nav bar
    const topnav = document.querySelector('header, [class*="topnav" i], [class*="TopNav" i], [class*="AppBar" i]');
    result.topnav = getComputed(topnav);
    if (topnav) result.topnavHeight = topnav.getBoundingClientRect().height;

    // Page heading
    const h1 = document.querySelector('h1, [class*="PageTitle" i]');
    result.pageHeading = getComputed(h1);

    // Body text
    const body = document.querySelector('p, [class*="description" i], [class*="subtitle" i]');
    result.bodyText = getComputed(body);

    // Primary button
    const primaryBtn = document.querySelector('button[class*="contained" i], button[class*="Primary" i], [class*="MuiButton-contained"]');
    result.primaryButton = getComputed(primaryBtn);

    // Outlined button
    const outlinedBtn = document.querySelector('button[class*="outlined" i], [class*="MuiButton-outlined"]');
    result.outlinedButton = getComputed(outlinedBtn);

    // Table header
    const th = document.querySelector('th');
    result.tableHeader = getComputed(th);

    // Table cell
    const td = document.querySelector('td');
    result.tableCell = getComputed(td);

    // Info banner
    const infoBanner = document.querySelector('[class*="alert" i], [class*="Alert" i], [role="alert"]');
    result.infoBanner = getComputed(infoBanner);

    // Card
    const card = document.querySelector('[class*="Paper" i], [class*="Card" i]');
    result.card = getComputed(card);

    // Input field
    const input = document.querySelector('input[type="text"], input[placeholder]');
    result.inputField = getComputed(input);

    // Page bg
    result.pageBg = getComputedStyle(document.body).backgroundColor;
    result.mainBg = getComputed(document.querySelector('main, [class*="content" i]:not(nav *)'));

    return result;
  });

  // Write metrics to file
  fs.writeFileSync(
    path.join(DIR, '_css-metrics.json'),
    JSON.stringify(metrics, null, 2)
  );
  console.log('  CSS metrics saved to _css-metrics.json');

  // ========================================================================
  // DONE
  // ========================================================================
  await browser.close();
  console.log(`\nDone. ${shotIndex} screenshots saved to ${DIR}/`);
})();
