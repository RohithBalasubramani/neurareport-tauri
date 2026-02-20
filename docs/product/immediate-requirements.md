# Immediate UI Requirements

This spec captures the current front-end expectations for the Setup experience. It reflects the implementation in `frontend/src/pages/Setup` and should be treated as the single source of truth for layout and behaviour notes until design handoff.

## 1. Global Layout
- Sticky top bar across the app. Content panes sit directly beneath it (no vertical centering).
- Setup page uses a fixed 25% / 75% split on desktop: left navigation rail (25%), working area (75%).
- Use tight top/bottom padding so content starts immediately after the bar.

## 2. Left Navigation (Setup)
- Three stacked, full-width buttons:
  1. `CONNECT`
  2. `UPLOAD & VERIFY`
  3. `RUN REPORTS`
- Buttons swap the right pane; no combined or accordion layouts.
- The rail is navigation-only. State for each screen lives in its respective pane.

## 3. Progress Indicator (Generate Screen Only)
- Replace the old multi-step wizard with a non-interactive indicator shown only on `UPLOAD & VERIFY`.
- Steps (auto-ticked as backend events fire):
  1. Upload & Verify
  2. Generate Mapping
  3. Approve
- Indicator is status only; user cannot click to jump between steps.

## 4. CONNECT Screen (Right Pane)
- Form fields: DB type, host, port, database, username, password toggle, SSL toggle.
- Actions:
  - `Test Connection` -> inline status with message.
  - `Save` (enabled only after a successful test) -> toast on success.
- Saved connections table (visible when at least one record exists):
  - Columns: Name | DB Type | Host | Database | Status | Last Connected | Actions.
  - Row actions:
    - `Select` -> sets active connection with confirmation toast.
    - `Test` -> reruns health check, updates status chip and inline message (`Test performed`).
    - `Edit` -> loads row into the form; saving updates the record.
    - `Delete` -> confirmation modal + success toast.
- `Change Connection` affordance exists here by default. Outside this screen it only appears when creating a new template (see below).

## 5. UPLOAD & VERIFY Screen
- Top: progress indicator (see section 3), pinned below the header.
- Upload block:
  - Drag-and-drop card with fallback button.
  - `Verify Template` triggers modal with dim backdrop and stage progress. Success closes modal with an affirmative state.
- Mapping block:
  - After verification succeeds, enable `Generate Mapping`.
  - While running, show inline loader panel (no modal) with determinate progress when available.
- Approve block:
  - When mapping finishes, surface `Approve` modal (preview left, placeholders list right).
  - `Approve & Save` adds template to Templates screen; show toast.
- `Change Connection` link/button appears in this screen only (since switching resets the upload flow). On click, show warning text: "Switching connections resets current upload and verification state."

## 6. RUN REPORTS Screen
- Render responsive card grid (2-4 columns based on width).
- Card structure:
  - Large thumbnail at top (first page preview).
  - Heading immediately below thumbnail (single line, ellipsis + tooltip on overflow).
  - Tags row (chips) under heading.
  - File-type badge/dropdown at top-right of card frame.
  - Dummy `Edit` icon top-right (non-functional placeholder).
- No `Change Connection` UI on this screen.

## 7. Navigation & Compatibility Rules
- Navigating from RUN REPORTS to UPLOAD & VERIFY preserves current connection selection.
- Changing the connection mid-flow on UPLOAD & VERIFY resets mapping state and shows warning message.
- When a saved template is opened with a different active connection, surface a schema compatibility banner (informational only).

## 8. Feedback & Micro-Interactions
- Every action produces immediate feedback:
  - `Test` -> inline `Test performed` message + status chip update.
  - `Save` / `Select` / `Delete` / `Approve` -> brief toasts (success or error).
- Buttons remain disabled until prerequisites are satisfied (e.g. Save disabled until Test passes).
- Modals must trap focus. Non-destructive modals close on `Esc`. Approve requires explicit confirmation.

## 9. Responsiveness
- Left navigation remains 25% width down to ~1280px viewport.
- Below that, collapse nav to horizontal tabs or drawer (behaviour must remain consistent across pages).
- Card grid auto-wraps; thumbnails maintain aspect ratio; headings truncate with tooltip.

## 10. Acceptance Checklist
- [ ] Sticky top bar, content starts immediately underneath.
- [ ] Setup uses 25% navigation rail / 75% content with stacked buttons `CONNECT`, `UPLOAD & VERIFY`, `RUN REPORTS`.
- [ ] Progress indicator visible only on `UPLOAD & VERIFY`, reflects Upload -> Mapping -> Approve stages, non-interactive.
- [ ] `Change Connection` present on CONNECT by default, and on UPLOAD & VERIFY with reset warning; absent elsewhere.
- [ ] Saved connections table supports Select/Test/Edit/Delete with clear inline feedback.
- [ ] Templates grid cards include thumbnail, heading, tags, file-type badge, and dummy Edit icon.
- [ ] All modals are accessible (focus trap, `Esc` behaviour) and actions emit toasts or inline status.
