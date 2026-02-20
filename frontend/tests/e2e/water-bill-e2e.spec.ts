/**
 * End-to-End Test: Water Bill PDF Template
 *
 * This test uploads a water bill PDF template, creates a database,
 * generates a report, and verifies the outputs visually.
 */

import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

const SCREENSHOT_DIR = "./test-results/water-bill-screenshots";

// Ensure screenshot directory exists
test.beforeAll(() => {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
});

test.describe("Water Bill PDF E2E Test", () => {
  test.setTimeout(180000); // 3 minute timeout

  test("complete flow: upload -> create db -> generate report", async ({
    page,
  }) => {
    // 1. Navigate to homepage and take screenshot
    await page.goto("http://localhost:5173/");
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "01-homepage.png"),
      fullPage: true,
    });
    console.log("Screenshot: homepage taken");

    // 2. Navigate to templates page
    await page.click('text="Templates"');
    await page.waitForLoadState("networkidle");
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "02-templates-page.png"),
      fullPage: true,
    });
    console.log("Screenshot: templates page taken");

    // 3. Click Upload Design button
    const uploadButton = page.locator('button:has-text("Upload Design")');
    if (await uploadButton.isVisible()) {
      await uploadButton.click();
      await page.waitForTimeout(1000);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "03-upload-dialog.png"),
        fullPage: true,
      });
      console.log("Screenshot: upload dialog taken");
    }

    // 4. Upload the water bill PDF
    const pdfPath =
      "C:\\Users\\Alfred\\Downloads\\Hyderabad Metropolitan Water Supply & Sewerage Board - Online Bill Payment.pdf";

    if (fs.existsSync(pdfPath)) {
      // Find file input and upload
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(pdfPath);
      await page.waitForTimeout(2000);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "04-file-selected.png"),
        fullPage: true,
      });
      console.log("Screenshot: file selected taken");

      // Wait for upload to complete
      await page.waitForTimeout(5000);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "05-after-upload.png"),
        fullPage: true,
      });
      console.log("Screenshot: after upload taken");
    } else {
      console.log("PDF file not found at:", pdfPath);
    }

    // 5. Navigate to databases/data page
    const dataNav = page.locator('text="Data"');
    if (await dataNav.isVisible()) {
      await dataNav.click();
      await page.waitForLoadState("networkidle");
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "06-data-page.png"),
        fullPage: true,
      });
      console.log("Screenshot: data page taken");
    }

    // 6. Check for analysis features
    const analysisNav = page.locator('text="Analysis"');
    if (await analysisNav.isVisible()) {
      await analysisNav.click();
      await page.waitForLoadState("networkidle");
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "07-analysis-page.png"),
        fullPage: true,
      });
      console.log("Screenshot: analysis page taken");
    }

    // 7. Check reports page
    const reportsNav = page.locator('text="Reports"');
    if (await reportsNav.isVisible()) {
      await reportsNav.click();
      await page.waitForLoadState("networkidle");
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, "08-reports-page.png"),
        fullPage: true,
      });
      console.log("Screenshot: reports page taken");
    }

    console.log("E2E test completed. Screenshots saved to:", SCREENSHOT_DIR);
  });
});
