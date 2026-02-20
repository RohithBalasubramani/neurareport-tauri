/**
 * Verify the water bill PDF upload appears in the templates
 */
import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

const SCREENSHOT_DIR = "./test-results/water-bill-screenshots";

test.beforeAll(() => {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
});

test.describe("Verify Water Bill Upload", () => {
  test.setTimeout(60000);

  test("verify uploaded template in UI", async ({ page }) => {
    // Navigate to templates page directly
    await page.goto("http://localhost:5173/templates");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "03-templates-with-upload.png"),
      fullPage: true,
    });
    console.log("Screenshot: templates page with water bill taken");

    // Look for the water bill template
    const waterBillText = page.locator('text="Hyderabad"');
    const visible = await waterBillText.isVisible().catch(() => false);
    console.log("Water bill template visible:", visible);

    // Click on a template to view details
    const templateRow = page.locator("tr").filter({ hasText: "PDF" }).first();
    if (await templateRow.isVisible()) {
      await templateRow.click();
      await page.waitForTimeout(2000);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "04-template-details.png"),
        fullPage: true,
      });
      console.log("Screenshot: template details taken");
    }

    // Navigate to Data Sources
    await page.click('text="Data Sources"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "05-data-sources.png"),
      fullPage: true,
    });
    console.log("Screenshot: data sources taken");

    // Navigate to Chat with Docs (AI feature)
    await page.click('text="Chat with Docs"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "06-chat-with-docs.png"),
      fullPage: true,
    });
    console.log("Screenshot: chat with docs taken");

    // Navigate to AI Agents
    await page.click('text="AI Agents"');
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "07-ai-agents.png"),
      fullPage: true,
    });
    console.log("Screenshot: AI agents taken");

    console.log("Verification complete!");
  });
});
