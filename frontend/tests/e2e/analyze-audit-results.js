#!/usr/bin/env node

/**
 * Audit Results Analysis Tool
 *
 * Analyzes the Action Resolution Ledger and generates detailed reports.
 *
 * Usage:
 *   node analyze-audit-results.js
 */

const fs = require('fs');
const path = require('path');

const EVIDENCE_DIR = path.join(__dirname, 'evidence', 'semantic-audit');
const LEDGER_PATH = path.join(EVIDENCE_DIR, 'ledger', 'ACTION-RESOLUTION-LEDGER.json');
const DEFECTS_PATH = path.join(EVIDENCE_DIR, 'defects', 'DEFECT-LIST.json');

console.log('\n' + '='.repeat(80));
console.log('SEMANTIC AUDIT RESULTS ANALYSIS');
console.log('='.repeat(80) + '\n');

// Check if ledger exists
if (!fs.existsSync(LEDGER_PATH)) {
  console.error('❌ Ledger not found at:', LEDGER_PATH);
  console.error('Run the audit first: npx playwright test audit-semantic-verification.spec.ts');
  process.exit(1);
}

// Load data
const ledger = JSON.parse(fs.readFileSync(LEDGER_PATH, 'utf-8'));
const defects = fs.existsSync(DEFECTS_PATH)
  ? JSON.parse(fs.readFileSync(DEFECTS_PATH, 'utf-8'))
  : { totalDefects: 0, defects: [] };

// Overall statistics
console.log('OVERALL STATISTICS');
console.log('-'.repeat(80));
console.log(`Total actions in inventory:    ${ledger.totalActionsInInventory || 0}`);
console.log(`Actions executed:               ${ledger.actionsExecuted || 0}`);
console.log(`Passed:                         ${ledger.passed || 0}`);
console.log(`Failed:                         ${ledger.failed || 0}`);
console.log(`Untestable:                     ${ledger.untestable || 0} (should be 0)`);
console.log(`Pass rate:                      ${(((ledger.passed || 0) / (ledger.actionsExecuted || 1)) * 100).toFixed(1)}%`);
console.log(`Coverage:                       ${(((ledger.actionsExecuted || 0) / (ledger.totalActionsInInventory || 1)) * 100).toFixed(1)}%`);
console.log('');

// Results by page
console.log('RESULTS BY PAGE');
console.log('-'.repeat(80));

const byPage = {};
ledger.results.forEach(r => {
  if (!byPage[r.page]) {
    byPage[r.page] = { total: 0, passed: 0, failed: 0 };
  }
  byPage[r.page].total++;
  if (r.verdict === 'PASS') byPage[r.page].passed++;
  else byPage[r.page].failed++;
});

const pageStats = Object.entries(byPage)
  .map(([page, stats]) => ({
    page,
    ...stats,
    passRate: ((stats.passed / stats.total) * 100).toFixed(1)
  }))
  .sort((a, b) => parseFloat(a.passRate) - parseFloat(b.passRate));

pageStats.forEach(stat => {
  const bar = '█'.repeat(Math.round(parseFloat(stat.passRate) / 5));
  console.log(
    `${stat.page.padEnd(25)} | ` +
    `${String(stat.passed).padStart(4)} / ${String(stat.total).padStart(4)} | ` +
    `${String(stat.passRate).padStart(5)}% | ` +
    `${bar}`
  );
});
console.log('');

// Defect categories
if (defects.totalDefects > 0) {
  console.log('DEFECT CATEGORIES');
  console.log('-'.repeat(80));

  const categories = {
    'Missing backend call': 0,
    'Backend response mismatch': 0,
    'Unstable selector': 0,
    'Execution failure': 0,
    'Semantic mismatch': 0,
    'Other': 0
  };

  defects.defects.forEach(d => {
    const desc = d.defectDescription || '';
    if (desc.includes('No backend call observed') && desc.includes('mutation')) {
      categories['Missing backend call']++;
    } else if (desc.includes('lacks') || desc.includes('empty body') || desc.includes('no job_id')) {
      categories['Backend response mismatch']++;
    } else if (desc.includes('unstable selector') || desc.includes('not relocatable')) {
      categories['Unstable selector']++;
    } else if (desc.includes('interaction failed') || desc.includes('exception')) {
      categories['Execution failure']++;
    } else if (desc.includes('Backend behavior mismatch')) {
      categories['Semantic mismatch']++;
    } else {
      categories['Other']++;
    }
  });

  Object.entries(categories)
    .filter(([_, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .forEach(([category, count]) => {
      const pct = ((count / defects.totalDefects) * 100).toFixed(1);
      console.log(`  ${category.padEnd(30)} : ${String(count).padStart(4)} (${pct}%)`);
    });
  console.log('');
}

// Top defects by frequency
if (defects.totalDefects > 0) {
  console.log('TOP 10 DEFECTS');
  console.log('-'.repeat(80));

  const defectsByDescription = {};
  defects.defects.forEach(d => {
    const key = d.defectDescription || 'Unknown';
    defectsByDescription[key] = (defectsByDescription[key] || 0) + 1;
  });

  const sortedDefects = Object.entries(defectsByDescription)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  sortedDefects.forEach(([desc, count], i) => {
    console.log(`${String(i + 1).padStart(2)}. [${count}x] ${desc.substring(0, 70)}`);
  });
  console.log('');
}

// Verification method breakdown
console.log('VERIFICATION METHODS USED');
console.log('-'.repeat(80));

const verificationMethods = {};
ledger.results.forEach(r => {
  const method = r.verificationMethod || 'Unknown';
  verificationMethods[method] = (verificationMethods[method] || 0) + 1;
});

Object.entries(verificationMethods)
  .sort((a, b) => b[1] - a[1])
  .forEach(([method, count]) => {
    const pct = ((count / ledger.actionsExecuted) * 100).toFixed(1);
    console.log(`  ${method.padEnd(40)} : ${String(count).padStart(4)} (${pct}%)`);
  });
console.log('');

// Pages with most defects
if (defects.totalDefects > 0) {
  console.log('PAGES WITH MOST DEFECTS');
  console.log('-'.repeat(80));

  const defectsByPage = {};
  defects.defects.forEach(d => {
    defectsByPage[d.page] = (defectsByPage[d.page] || 0) + 1;
  });

  Object.entries(defectsByPage)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([page, count]) => {
      const total = byPage[page]?.total || 0;
      const rate = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
      console.log(`  ${page.padEnd(25)} : ${String(count).padStart(4)} defects (${rate}% failure rate)`);
    });
  console.log('');
}

// Sample successful actions
console.log('SAMPLE SUCCESSFUL ACTIONS (First 5)');
console.log('-'.repeat(80));
const passed = ledger.results.filter(r => r.verdict === 'PASS').slice(0, 5);
passed.forEach(r => {
  console.log(`  ${r.actionId.padEnd(20)} | ${r.page.padEnd(15)} | ${r.uiDescription.substring(0, 40)}`);
});
console.log('');

// Sample failed actions
if (defects.totalDefects > 0) {
  console.log('SAMPLE FAILED ACTIONS (First 5)');
  console.log('-'.repeat(80));
  defects.defects.slice(0, 5).forEach(d => {
    console.log(`  ${d.actionId.padEnd(20)} | ${d.page.padEnd(15)} | ${d.uiDescription.substring(0, 40)}`);
    console.log(`    → ${d.defectDescription?.substring(0, 70) || 'No description'}`);
  });
  console.log('');
}

// File locations
console.log('OUTPUT FILES');
console.log('-'.repeat(80));
console.log(`  Ledger:           ${LEDGER_PATH}`);
if (defects.totalDefects > 0) {
  console.log(`  Defects:          ${DEFECTS_PATH}`);
}
console.log(`  Network captures: ${path.join(EVIDENCE_DIR, 'network')}`);
console.log(`  Screenshots:      ${path.join(EVIDENCE_DIR, 'screenshots')}`);
console.log('');

// Final assertion check
const assertionPath = path.join(EVIDENCE_DIR, 'FINAL-ASSERTION.json');
if (fs.existsSync(assertionPath)) {
  const assertion = JSON.parse(fs.readFileSync(assertionPath, 'utf-8'));
  console.log('FINAL ASSERTION');
  console.log('-'.repeat(80));
  assertion.statement.forEach(s => console.log(`  ✓ ${s}`));
  console.log('');
  console.log(`  Coverage: ${assertion.coverage.coveragePercentage}`);
  console.log(`  Pass rate: ${assertion.results.passRate}`);
  console.log('');
}

// Warnings
console.log('AUDIT VALIDATION');
console.log('-'.repeat(80));

const warnings = [];

if (ledger.untestable > 0) {
  warnings.push(`⚠ Found ${ledger.untestable} untestable actions (should be 0)`);
}

if (ledger.actionsExecuted < ledger.totalActionsInInventory) {
  const missing = ledger.totalActionsInInventory - ledger.actionsExecuted;
  warnings.push(`⚠ Incomplete: ${missing} actions not executed`);
}

if (defects.totalDefects === 0 && ledger.actionsExecuted > 100) {
  warnings.push(`⚠ Zero defects found (statistically suspicious for ${ledger.actionsExecuted} actions)`);
}

const clickOnlyPass = ledger.results.filter(r =>
  r.verdict === 'PASS' &&
  r.verificationMethod === 'None' &&
  !r.actualBackendBehavior.includes('expected')
).length;

if (clickOnlyPass > 0) {
  warnings.push(`⚠ ${clickOnlyPass} actions passed with insufficient verification`);
}

if (warnings.length > 0) {
  warnings.forEach(w => console.log(`  ${w}`));
  console.log('');
  console.log('  ❌ AUDIT INVALID - Address warnings above');
} else {
  console.log('  ✅ All validation checks passed');
  console.log('  ✅ Zero untestable actions');
  console.log('  ✅ All actions executed');
  console.log('  ✅ Backend verification complete');
}

console.log('');
console.log('='.repeat(80));
console.log('END OF ANALYSIS');
console.log('='.repeat(80) + '\n');

// Generate detailed CSV export
const csvPath = path.join(EVIDENCE_DIR, 'audit-results.csv');
const csvRows = [
  'Action ID,Page,Route,UI Description,Intended Behavior,Actual Behavior,Verification Method,Verdict,Defect Description,Execution Time (ms)'
];

ledger.results.forEach(r => {
  csvRows.push([
    r.actionId,
    r.page,
    r.route,
    `"${(r.uiDescription || '').replace(/"/g, '""')}"`,
    `"${(r.intendedBackendLogic || '').replace(/"/g, '""')}"`,
    `"${(r.actualBackendBehavior || '').replace(/"/g, '""')}"`,
    r.verificationMethod,
    r.verdict,
    `"${(r.defectDescription || '').replace(/"/g, '""')}"`,
    r.executionTimeMs
  ].join(','));
});

fs.writeFileSync(csvPath, csvRows.join('\n'));
console.log(`CSV export saved: ${csvPath}\n`);
