/**
 * Comprehensive E2E Test for NeuraReport
 *
 * Tests the application using existing templates and data sources.
 */

import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

const SCREENSHOT_DIR = "./test-results/e2e-screenshots";

test.beforeAll(() => {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
});

test.describe("NeuraReport E2E Comprehensive Test", () => {
  test.setTimeout(120000); // 2 minute timeout

  test("complete application walkthrough", async ({ page }) => {
    // 1. Dashboard
    await page.goto("http://localhost:5173/");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "01-dashboard.png"),
      fullPage: true,
    });
    console.log("Screenshot: Dashboard");

    // 2. Templates Page
    await page.click('text="Templates"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "02-templates.png"),
      fullPage: true,
    });
    console.log("Screenshot: Templates");

    // 3. Click on a template to view details
    const firstTemplate = page.locator("tr").filter({ hasText: "PDF" }).first();
    if (await firstTemplate.isVisible()) {
      await firstTemplate.click();
      await page.waitForTimeout(1500);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "03-template-details.png"),
        fullPage: true,
      });
      console.log("Screenshot: Template Details");
    }

    // 4. My Reports page
    await page.click('text="My Reports"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "04-my-reports.png"),
      fullPage: true,
    });
    console.log("Screenshot: My Reports");

    // 5. Running Jobs - use first() to handle multiple matches
    const runningJobs = page.locator('text="Running Jobs"').first();
    if (await runningJobs.isVisible()) {
      await runningJobs.click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(1000);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "05-running-jobs.png"),
        fullPage: true,
      });
      console.log("Screenshot: Running Jobs");
    }

    // 6. Data Sources
    await page.click('text="Data Sources"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "06-data-sources.png"),
      fullPage: true,
    });
    console.log("Screenshot: Data Sources");

    // 7. Chat with Docs (AI Assistant)
    await page.click('text="Chat with Docs"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "07-chat-with-docs.png"),
      fullPage: true,
    });
    console.log("Screenshot: Chat with Docs");

    // 8. AI Agents
    await page.click('text="AI Agents"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "08-ai-agents.png"),
      fullPage: true,
    });
    console.log("Screenshot: AI Agents");

    // 9. Knowledge Base
    await page.click('text="Knowledge Base"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "09-knowledge-base.png"),
      fullPage: true,
    });
    console.log("Screenshot: Knowledge Base");

    // 10. Search functionality
    const search = page.locator('input[placeholder*="Search"]').first();
    if (await search.isVisible()) {
      await search.click();
      await page.waitForTimeout(500);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "10-search.png"),
        fullPage: true,
      });
      console.log("Screenshot: Search");
    }

    // Summary
    console.log("\n=== E2E Test Summary ===");
    console.log("Screenshots saved to:", SCREENSHOT_DIR);
    console.log("Tests completed successfully!");
  });
});
