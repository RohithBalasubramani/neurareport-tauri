import { test, expect } from '@playwright/test';
import path from 'path';

const BASE = 'http://100.90.185.31:9071';
const SAMPLE_DIR = '/home/rohith/desktop/NeuraReport/test_excel_samples';

test.describe('Visualization Excel Upload + Diagram Generation', () => {
  test('upload Excel, see table, generate flowchart with mermaid', async ({ page }) => {
    await page.goto(`${BASE}/visualization`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Upload flowchart_steps.xlsx
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(SAMPLE_DIR, 'flowchart_steps.xlsx'));
    await page.waitForTimeout(3000);

    // Verify table appears
    await page.screenshot({ path: '/tmp/viz-test-01-table.png', fullPage: true });
    const tableCount = await page.locator('table').count();
    console.log('Table count after upload:', tableCount);
    expect(tableCount).toBeGreaterThan(0);

    // Click "Generate Flowchart" button in the main area
    const generateBtn = page.locator('button:has-text("Generate Flowchart")');
    console.log('Generate button visible:', await generateBtn.isVisible());

    // Listen for API response
    const apiPromise = page.waitForResponse(
      (resp) => resp.url().includes('/diagrams/flowchart'),
      { timeout: 15000 }
    );

    await generateBtn.click();

    const resp = await apiPromise;
    const body = await resp.json();
    console.log('API response keys:', Object.keys(body));
    console.log('Has mermaid_code:', !!body.mermaid_code);
    console.log('mermaid_code preview:', body.mermaid_code?.substring(0, 200));

    // Wait for mermaid to render
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/viz-test-02-diagram.png', fullPage: true });

    // Check if SVG was rendered by mermaid
    const svgCount = await page.locator('.mermaid svg, [data-mermaid] svg, svg[id^="mermaid"]').count();
    const anySvg = await page.locator('svg').count();
    console.log('Mermaid SVG count:', svgCount);
    console.log('Any SVG count:', anySvg);

    // Check visible text for diagram elements
    const bodyText = await page.locator('body').innerText();
    const hasDiagramText = bodyText.includes('Start') || bodyText.includes('Validate');
    console.log('Has diagram text (Start/Validate):', hasDiagramText);
  });

  test('upload org_chart.xlsx, generate flowchart', async ({ page }) => {
    await page.goto(`${BASE}/visualization`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Select Org Chart type
    await page.locator('text=Org Chart').click();
    await page.waitForTimeout(500);

    // Upload org chart data
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(SAMPLE_DIR, 'org_chart.xlsx'));
    await page.waitForTimeout(3000);

    // Click Generate
    const generateBtn = page.locator('button:has-text("Generate Org Chart")');
    const apiPromise = page.waitForResponse(
      (resp) => resp.url().includes('/diagrams/'),
      { timeout: 15000 }
    );
    await generateBtn.click();

    const resp = await apiPromise;
    const body = await resp.json();
    console.log('Org chart mermaid_code:', body.mermaid_code?.substring(0, 300));

    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/viz-test-03-orgchart.png', fullPage: true });
  });

  test('upload sequence_diagram.xlsx, generate sequence', async ({ page }) => {
    await page.goto(`${BASE}/visualization`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Select Sequence Diagram type
    await page.locator('text=Sequence Diagram').click();
    await page.waitForTimeout(500);

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(SAMPLE_DIR, 'sequence_diagram.xlsx'));
    await page.waitForTimeout(3000);

    const generateBtn = page.locator('button:has-text("Generate Sequence")');
    const apiPromise = page.waitForResponse(
      (resp) => resp.url().includes('/diagrams/'),
      { timeout: 15000 }
    );
    await generateBtn.click();

    const resp = await apiPromise;
    const body = await resp.json();
    console.log('Sequence mermaid_code:', body.mermaid_code?.substring(0, 300));

    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/viz-test-04-sequence.png', fullPage: true });
  });
});
