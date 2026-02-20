# NeuraReport UI Audit Report

**Date:** 2026-02-17
**Viewport:** 1440 x 900 @ 1x (primary), 1024px, 768px (responsive)
**Base URL:** http://127.0.0.1:5180/neurareport
**Screenshots:** 229 captured via Playwright interactive audit
**Audit Tool:** audit-interactive.js (Playwright headless Chromium)

---

## 1. VISUAL PARAMETERS

### A. Size (Width, Height, Padding, Margin, Font-size, Icon-size, Border-thickness)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-S1 | Analyze page renders at compressed scale | MEDIUM | `/analyze` (055-056) | Entire page renders visibly smaller than all other pages. Font sizes, dropdowns, and drop zone appear ~80% scale compared to e.g. Connections or Reports. |
| V-S2 | Sidebar measured width includes content area | LOW | All pages | CSS metrics report `sidebarWidth: 526px` — this includes the sidebar + main content container. Actual sidebar rail is ~240px expanded. |
| V-S3 | TopNav height = 57px | INFO | All pages | Consistent across all pages. Matches expectation. |
| V-S4 | Jobs table Job ID column wraps to 2 lines | LOW | `/jobs` (038) | UUID values like `0868dd32-89a...` wrap to two lines within the narrow Job ID column. Consider `white-space: nowrap` or truncating with tooltip. |
| V-S5 | Agent cards inconsistent grid rhythm | LOW | `/agents` (127-128) | Cards use 2+3+1 layout (Research + Data Analyst on row 1, Email + Content + Proofread on row 2, Report Analyst alone on row 3). Last card orphaned. |

### B. Color (Background, Text, Border, Icon, Hover, Active, Disabled, Focus, Status)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-C1 | Page background consistent | PASS | All pages | `rgb(253, 253, 252)` (#fdfdfc) matches warm neutral palette across all pages. |
| V-C2 | Primary button uses dark instead of brand blue | LOW | `/docqa` (097) | "Create Your First Session" CTA uses `#111827` (dark gray-black) bg. This is the app's standard primary button color, but differs from the blue used in Synthesis (`+ New Session`) and Federation (`+ New Virtual Schema`). Inconsistency in primary CTA colors. |
| V-C3 | Status badge colors | PASS | `/connections` (016) | Connected = green check `#22c55e`, Unknown = red exclamation `#ef4444`. Consistent across table. |
| V-C4 | Confidence/Reversible badge colors | PASS | `/analyze`, `/summary`, `/enrichment` | Orange "Confidence: Review required", Green "Reversible: No source changes" / "Original data unchanged". Consistent AI disclaimer badges. |
| V-C5 | Ops Console uses blue CTA buttons | INFO | `/ops` (076) | "Register User" and "Get Access Token" use `rgb(59, 130, 246)` blue, different from the dark primary buttons elsewhere. This is intentional differentiation for ops/admin actions. |
| V-C6 | TopNav background semi-transparent | INFO | All pages | `rgba(255, 255, 255, 0.85)` — frosted glass effect. Works well. |
| V-C7 | Info banner consistent | PASS | Connections, Jobs, History, Schedules | Warm neutral bg `#fdfdfc`, border `#d4d2cc`, radius 8px. Consistent across all info banners. |

### C. Typography (Font-family, Weight, Size, Line-height, Letter-spacing, Alignment, Transform)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-T1 | "(O ptio na l)" letter-spacing bug | MEDIUM | `/analyze-legacy` (060) | Dropdown labels for "Analyze from Connection" and "Report Template" show broken letter-spacing in the "(Optional)" suffix. Letters are visibly split: "O ptio na l". |
| V-T2 | Font family consistent | PASS | All pages | Inter used throughout for body/UI text. Space Grotesk used for some headings (body text metrics: `"Space Grotesk", Inter`). |
| V-T3 | Body text hierarchy | PASS | All pages | Page headings: 20px/500, Table headers: 14px/500, Table cells: 14px/400, Info banners: 12.25px/400, Sidebar items: 12.25px/400. Consistent type scale. |
| V-T4 | Section headers use UPPERCASE + letter-spacing | PASS | Multiple pages | "HOME", "REPORTS", "DATA" sidebar groups; "BASIC INFORMATION", "SCHEDULE TIMING" in dialogs; "COLLECTIONS", "TAGS" in Knowledge. Consistent section label pattern. |

### D. Spacing (Padding, Margin, Gap, Section-spacing, Scale)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-SP1 | Table cell padding consistent | PASS | All tables | `padding: 0px 16px` for both headers and cells. |
| V-SP2 | Info banner padding consistent | PASS | All banners | `padding: 12px 16px`, `margin: 0px 0px 16px`. |
| V-SP3 | Primary button padding | PASS | All pages | `padding: 6px 16px` for contained buttons. |
| V-SP4 | Card padding | PASS | Knowledge, Brand Kit, Agents | `padding: 20px 16px` for card components. |

### E. Shape (Border-radius, Shadow, Elevation, Stroke)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-SH1 | Border radius scale | PASS | All pages | 8px used consistently for buttons, banners, cards, dialogs. |
| V-SH2 | Primary button shadow | INFO | All pages | `box-shadow: rgba(0, 0, 0, 0.15) 0px 4px 14px 0px` — subtle elevation on primary contained buttons. |
| V-SH3 | Outlined buttons flat | PASS | All pages | `box-shadow: none` for outlined/secondary buttons. Clean differentiation from primary. |
| V-SH4 | Dialog borders | PASS | All dialogs (020, 053, 118, 177) | Dialogs render with neutral border, 8px radius, proper backdrop blur. |

### F. Layout (Position, Z-index, Alignment, Flex/Grid, Breakpoints)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-L1 | Summary dropdown text overlap | MEDIUM | `/summary` (100) | First dropdown shows "Select a completed..." and "report to summarize..." text overlapping. The placeholder text and label collision creates unreadable text. |
| V-L2 | Templates table column clipped | MEDIUM | `/templates` (026-027) | At 1440px, the rightmost column is partially clipped at viewport edge with partial characters visible. |
| V-L3 | Dashboard sidebar collapsed by default | MEDIUM | `/` (001-003) | Dashboard opens with sidebar in partially collapsed state while all other pages show expanded sidebar. Inconsistent default state. |
| V-L4 | Sidebar collapse indicator | LOW | Collapsed sidebar (208-209) | A small blue sliver/indicator visible on left edge when sidebar is collapsed. Minor visual artifact. |

### G. Motion (Transitions, Easing, Animations)

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| V-M1 | Sidebar collapse animation | PASS | Sidebar (207-210) | Smooth collapse/expand transition. Content shifts cleanly. |
| V-M2 | Loading spinner | PASS | `/widgets` (187) | Blue circular spinner with "Analyzing database schema and recommending widgets..." text. Clean loading state. |

---

## 2. STATE PARAMETERS

### Default State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-D1 | All 35 routes load without errors | PASS | All |
| S-D2 | Sidebar shows correct active state highlighting (dark bg) | PASS | All pages |
| S-D3 | TopNav renders consistently (breadcrumb, search, connection chip, icons) | PASS | All pages |
| S-D4 | Empty states have clear messaging and CTAs | PASS | Documents (104), Spreadsheets (107), Dashboards (110), Workflows (124) |
| S-D5 | Data-populated pages render data correctly | PASS | Connections (016), Templates (026), Jobs (038), History (068), Knowledge (154) |
| S-D6 | Wizard stepper shows proper step progression (1/2/3) | PASS | `/wizard` (188-192) |

### Hover State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-H1 | Sidebar item hover — subtle bg highlight | PASS | (003-006) |
| S-H2 | Table row hover — subtle row highlight, kebab menu appears | PASS | Connections (018-019), Templates (031-032) |
| S-H3 | Button hover states | PASS | All pages — verified on primary, outlined, and icon buttons |
| S-H4 | Card hover — Knowledge doc cards, Agent cards, Connector cards | PASS | (156-157, 129-134, 114-116) |
| S-H5 | Quick action hover on Dashboard | PASS | (013-014) |
| S-H6 | Star/favorite hover tooltip | PASS | Connections (025) — shows tooltip on hover |

### Active/Pressed State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-A1 | Tab selection active indicator (blue underline) | PASS | Stats (072-075), Enrichment (085, 090-091), Design (166-173), Search (138-143), Connectors (112, 120) |
| S-A2 | Time period chip selection | PASS | Reports (042-047) — "Today" button shows darker selected state |
| S-A3 | Agent card selection — border highlight | PASS | Agents (135) — selected card gets visible border |
| S-A4 | Ingestion method selection — dashed border outline | PASS | Ingestion (178-185) — selected method card gets border |
| S-A5 | Visualization type selection — highlight | PASS | Visualization (147-152) — selected type row highlighted |
| S-A6 | Schedule toggle active state | PASS | Schedules (050) — toggle shows active (dark blue) state |

### Focused State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-F1 | Search input focus | PASS | TopNav (010) — search bar shows focus highlight |
| S-F2 | Form input focus | PASS | Query Builder (083), Templates Chat (035), Connections search (023) |
| S-F3 | Agent Research Topic textarea focus | PASS | Agents (137) |
| S-F4 | Knowledge search focus | PASS | Knowledge (163) |
| S-F5 | Summary textarea focus | PASS | Summary (102) |

### Disabled State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-DI1 | Enrichment Preview/Enrich buttons disabled when no data | PASS | Enrichment (092) — buttons show reduced opacity |
| S-DI2 | Query Builder "Generate SQL" disabled without input | PASS | Query (082) — button appears grayed out |
| S-DI3 | Ingestion Import button disabled without URL | PASS | Ingestion URL Import (179) — Import button dim |

### Loading State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-L1 | Widget Intelligence loading spinner | PASS | Widgets (187) — circular spinner + text message |
| S-L2 | History page all reports show "Pending" status | INFO | History (068) — all entries show hourglass + Pending |

### Error State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-E1 | Connection "Unknown" status uses red badge | PASS | Connections (016-024) — red exclamation + "Unknown" text |
| S-E2 | Job "Failed" status uses red badge | PASS | Jobs (038) — red exclamation + "Failed" text |

### Success State

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| S-SU1 | Connection "Connected" status uses green badge | PASS | Connections (016) — green check + "Connected" |
| S-SU2 | Job "Completed" status uses green badge | PASS | Jobs (038) — green check + "Completed" + 100% |
| S-SU3 | Schedule "Active" status + running banner | PASS | Schedules (050) — green check banner "Scheduler running" |
| S-SU4 | TopNav connection chip green dot | PASS | All pages — "HMWSSB Billing DB" chip with green dot |

---

## 3. INTERACTION PARAMETERS

### Click Behavior

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| I-C1 | "New Report" sidebar click navigates to wizard | PASS | (012) → wizard page |
| I-C2 | Template row click navigates to Reports | PASS | Templates (033) → Reports page |
| I-C3 | Add Data Source opens dialog | PASS | Connections (020) — clean modal with form fields |
| I-C4 | Create Schedule opens dialog | PASS | Schedules (052-053) — full form with BASIC INFO, TIMING, EMAIL sections |
| I-C5 | Connector "Connect" opens connection dialog | PASS | Connectors PostgreSQL (118-119) — 6-field form |
| I-C6 | New Brand Kit opens dialog | PASS | Design (177) — Name, Description, Colors, Advanced |
| I-C7 | Filters dropdown opens | PASS | Connections (022) — STATUS + TYPE filter sections |
| I-C8 | TopNav shortcuts icon opens shortcuts dialog | PASS | (196-197) — shows Ctrl+K, Esc shortcuts |
| I-C9 | TopNav help icon opens help panel | PASS | (198-199) — 5 help options with Open buttons |
| I-C10 | TopNav user icon opens menu | PASS | (200-201) — Settings + Sign Out |
| I-C11 | TopNav jobs icon opens panel | PASS | (202-203) — shows jobs + downloads |
| I-C12 | TopNav connection chip click shows tooltip | PASS | (204-205) — "Database connected" tooltip |
| I-C13 | TopNav search shows results | PASS | (206) — search for "test" shows "Test HMWSSB Bill" with Template badge |
| I-C14 | DocQA session click loads conversation | PASS | (098) — shows AI response, sources, related questions, chat input |
| I-C15 | Agent history click navigates to History | PASS | (136) — navigates away rather than in-page |
| I-C16 | Knowledge collection click filters documents | PASS | Knowledge (158) — Marketing Assets shows 2 filtered docs |
| I-C17 | Reports AI Template Picker expandable | PASS | Reports (049) — chevron expands picker section |

### Scroll Behavior

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| I-SC1 | Dashboard scroll to bottom | PASS | (015) — Quick Actions section visible at bottom |
| I-SC2 | Settings scroll to System Status | PASS | Settings (065) — System Status section with "Healthy" badge |
| I-SC3 | Analyze fullpage scroll | PASS | (056) — compressed but complete |

### Input Validation

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| I-V1 | Required field markers (*) | PASS | Create Schedule (053) — Schedule Name*, Template*, Connection*, Start/End Date* |
| I-V2 | Character counter | PASS | Summary (100) — "0 / 50,000 characters" shown below textarea |
| I-V3 | Summary length slider | PASS | Summary (100) — "Summary Length: 5 sentences" |

### Feedback Timing

| # | Observation | Status | Pages |
|---|-------------|--------|-------|
| I-F1 | Connection chip tooltip on click | PASS | Instant tooltip "Database connected" |
| I-F2 | Favorite toggle tooltip | PASS | Connections (024) — "Remove from favorites" tooltip on click |

### Accessibility

| # | Issue | Severity | Pages |
|---|-------|----------|-------|
| I-A1 | Form labels present | PASS | All forms — Schedule, Connector, Brand Kit dialogs have proper labels |
| I-A2 | Keyboard shortcut info displayed | PASS | Shortcuts dialog (196) shows Ctrl+K, Esc |
| I-A3 | Breadcrumb navigation present | PASS | All pages — home > page name pattern in TopNav |

---

## 4. SYSTEM-LEVEL PARAMETERS

### Color Palette Consistency

| Token | Value | Status |
|-------|-------|--------|
| Page bg | `#fdfdfc` / `rgb(253, 253, 252)` | PASS — consistent across all pages |
| Primary text | `#111827` / `rgb(17, 24, 39)` | PASS |
| Secondary text | `#374151` / `rgb(55, 65, 81)` | PASS |
| Border | `#d4d2cc` / `rgb(212, 210, 204)` | PASS |
| Neutral 100 | `#f4f2ed` / `rgb(244, 242, 237)` | PASS (outlined button bg) |
| Primary button bg | `#111827` | PASS (dark contained buttons) |
| TopNav bg | `rgba(255, 255, 255, 0.85)` | PASS |
| Active tab | Blue underline | PASS |

### Typography Scale Consistency

| Level | Font | Size | Weight | Line-height | Status |
|-------|------|------|--------|-------------|--------|
| Page heading | Space Grotesk / Inter | 20px | 500 | normal | PASS |
| Table header | Inter | 14px | 500 | 21px | PASS |
| Table cell | Inter | 14px | 400 | 20px | PASS |
| Button text | Inter | 14px | 500 | 16px | PASS |
| Body/sidebar | Inter | 12.25px | 400 | 18.375px | PASS |
| Info banner | Inter | 12.25px | 400 | 20px | PASS |
| Input field | Inter | 14px | 400 | 20px | PASS |

### Spacing Scale Consistency

| Component | Padding | Status |
|-----------|---------|--------|
| Primary button | 6px 16px | PASS |
| Outlined button | 6px 12px | PASS |
| Table cells | 0px 16px | PASS |
| Info banner | 12px 16px | PASS |
| Card | 20px 16px | PASS |
| Input field | 6px 12px | PASS |

### Radius Scale Consistency

| Component | Radius | Status |
|-----------|--------|--------|
| Buttons | 8px | PASS |
| Info banners | 8px | PASS |
| TopNav | 8px | PASS |
| Dialogs | 8px | PASS |
| Cards | varies (0px measured, but visually rounded) | INFO |
| Table rows | 0px | PASS |

### Elevation Scale Consistency

| Level | Shadow | Usage | Status |
|-------|--------|-------|--------|
| Level 0 | none | Outlined buttons, tables, info banners | PASS |
| Level 1 | `rgba(0,0,0,0.15) 0px 4px 14px` | Primary contained buttons | PASS |
| Level 2 | Subtle card elevation | Dialogs, popovers | PASS |

### Breakpoint System

| Breakpoint | Behavior | Status |
|------------|----------|--------|
| 1440px (default) | Full sidebar + content, 6-col connector grid | PASS |
| 1024px | Sidebar visible but narrower, content adapts | PASS |
| 768px | Hamburger menu replaces sidebar, single-column tables | **ISSUES** |

#### 768px Responsive Issues:

| # | Issue | Severity | Pages | Details |
|---|-------|----------|-------|---------|
| R-1 | Connections table — Name column breaks to 15+ lines | HIGH | (224) | "Fixture 01 - OnlineInvoices Sample Invoice" wraps character-by-character vertically. Completely unreadable. Each letter on its own line. |
| R-2 | Templates table — columns severely truncated | HIGH | (225 from prior session) | Status shows "A...", date shows "Toda y", "2/16/2 026" with word-breaking. |
| R-3 | Connectors — grid reflows properly | PASS | (226) | 5-col database grid + 4-col cloud storage. Snowflake wraps to second row cleanly. |
| R-4 | Agents — cards stack vertically | PASS | (228) | Single column card layout works well at 768px. |
| R-5 | Knowledge — single column card list | PASS | (221 @ 1024px) | Cards stack in single column, sidebar remains. |
| R-6 | Dashboard — stat cards 2-col grid | PASS | (223 from prior session) | Hamburger menu, 2-col stat grid, Quick Actions visible. |

### Component Variant Consistency

| Component | Variants Found | Consistency |
|-----------|----------------|-------------|
| Primary button | Dark contained (`#111827`) | PASS — consistent everywhere except Ops (blue) |
| Outlined button | Neutral bg (`#f4f2ed`) | PASS |
| Info banner | Warm neutral bg + border | PASS — Connections, Jobs, History, Schedules, Reports |
| Table | Header + rows + pagination | PASS |
| Dialog/Modal | Title + subtitle + form + action buttons | PASS — Add Data Source, Create Schedule, Connect PostgreSQL, New Brand Kit all follow same pattern |
| Card | Title + description + actions | PASS |
| Tab navigation | Blue underline active tab | PASS — Stats, Enrichment, Design, Search, Connectors |
| Chips/Badges | Status badges (Connected/Failed/Active/Pending) | PASS |
| Dropzone | Dashed border + icon + text + formats | PASS — Ingestion, Analyze pages |
| Selection cards | Border highlight on select | PASS — Agents, Ingestion, Visualization |
| Empty state | Icon + title + description + CTA | PASS — Documents, Spreadsheets, Dashboards, Workflows |

---

## 5. SUMMARY OF ALL BUGS & ISSUES

### Critical / High Priority

| # | Issue | Page | Category |
|---|-------|------|----------|
| BUG-1 | 768px responsive: Connections table Name column breaks character-by-character, completely unreadable | `/connections` @ 768px | Layout, Breakpoints |
| BUG-2 | 768px responsive: Templates table columns severely truncated with word-breaking | `/templates` @ 768px | Layout, Breakpoints |

### Medium Priority

| # | Issue | Page | Category |
|---|-------|------|----------|
| BUG-3 | Summary dropdown text overlap — placeholder and label text collide | `/summary` | Layout, Typography |
| BUG-4 | Analyze Legacy "(O ptio na l)" broken letter-spacing in dropdown labels | `/analyze-legacy` | Typography |
| BUG-5 | Analyze page renders at compressed/smaller scale than all other pages | `/analyze` | Size, Layout |
| BUG-6 | Dashboard sidebar collapsed by default (inconsistent with all other pages) | `/` | Layout, Consistency |
| BUG-7 | Templates table rightmost column clipped at 1440px viewport | `/templates` | Layout, Size |

### Low Priority

| # | Issue | Page | Category |
|---|-------|------|----------|
| BUG-8 | Jobs table UUID column wraps to 2 lines | `/jobs` | Layout, Typography |
| BUG-9 | Agent cards 2+3+1 grid creates orphaned last card | `/agents` | Layout, Grid |
| BUG-10 | DocQA "Create Your First Session" CTA uses dark bg while similar CTAs elsewhere use blue | `/docqa` | Color, Consistency |
| BUG-11 | Sidebar collapse leaves small blue sliver indicator | Sidebar collapsed state | Layout, Visual |
| BUG-12 | Templates Chat AI panel gray background feels cooler than warm neutral palette | `/templates/new/chat` | Color |

### Fixed (This Session)

| # | Issue | Resolution |
|---|-------|------------|
| FIXED-1 | Bell/notification icon in TopNav across all pages | Removed `<NotificationCenter />` from TopNav.jsx and unused import from Sidebar.jsx |

---

## 6. PASSED AUDIT AREAS (No Issues Found)

- All 35 routes load without errors
- Font family consistency (Inter throughout, Space Grotesk for headings)
- Color palette alignment with NeurACT Desktop warm neutral theme
- All dialog/modal patterns consistent (Add Data Source, Create Schedule, Connect PostgreSQL, New Brand Kit)
- TopNav interactions all working (shortcuts, help, user menu, jobs panel, connection chip, search)
- Tab navigation patterns consistent across Stats, Enrichment, Design, Search, Connectors
- Empty states provide clear messaging and CTAs
- Status badges (Connected/Failed/Active/Pending/Unknown) use correct colors
- AI disclaimer banners (Source/Confidence/Reversible) consistent across AI-powered pages
- Info banners styling and spacing consistent
- Button hierarchy clear (primary dark contained vs outlined neutral)
- Ingestion method switching works correctly for all 7 methods
- Visualization type selection works for all 10 types
- Knowledge Library collection filtering works
- 404 page renders cleanly with Go Back + Go to Dashboard CTAs
- Wizard stepper shows proper step progression
- Form validation markers (required fields *) present
- Sidebar hover, active, and collapsed states all working
- Loading states (Widget Intelligence) properly shown

---

## 7. CSS DESIGN TOKEN REFERENCE (Extracted)

```json
{
  "colors": {
    "pageBg": "#fdfdfc",
    "primaryText": "#111827",
    "secondaryText": "#374151",
    "border": "#d4d2cc",
    "neutral100": "#f4f2ed",
    "primaryButtonBg": "#111827",
    "topnavBg": "rgba(255,255,255,0.85)",
    "outlinedButtonBorder": "rgba(212,210,204,0.2)"
  },
  "typography": {
    "fontFamily": "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
    "headingFamily": "Space Grotesk, Inter, system-ui, sans-serif",
    "heading": "20px / 500",
    "tableHeader": "14px / 500",
    "body": "14px / 400",
    "small": "12.25px / 400",
    "button": "14px / 500"
  },
  "spacing": {
    "buttonPadding": "6px 16px",
    "inputPadding": "6px 12px",
    "cellPadding": "0px 16px",
    "bannerPadding": "12px 16px",
    "cardPadding": "20px 16px"
  },
  "radius": {
    "default": "8px"
  },
  "elevation": {
    "primaryButton": "rgba(0,0,0,0.15) 0px 4px 14px",
    "flat": "none"
  },
  "layout": {
    "topnavHeight": "57px",
    "sidebarExpandedWidth": "~240px"
  }
}
```

---

**Total screenshots reviewed:** 229
**Issues found:** 12 (2 high, 5 medium, 5 low)
**Issues fixed this session:** 1 (bell icon)
**Passed checks:** 50+
