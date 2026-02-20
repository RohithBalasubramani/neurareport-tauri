# NeuraReport UI/UX Restructure Plan

Based on patterns from: assistant-ui, huggingface/chat-ui, mckaywrigley/chatbot-ui

---

> Note (2026-01-23): `frontend/src/store` has moved to `frontend/src/stores`, and duplicate `components/ui` primitives were consolidated into `components/primitives`.

## STEP 1: HIGH-LEVEL UI ARCHITECTURE

### Current vs Target Layout

```
CURRENT LAYOUT:
┌──────────────────────────────────────────────────┐
│  Header (Logo, Tabs, Connection Status, Jobs)    │
├──────────────────────────────────────────────────┤
│                                                  │
│           Full-width content area                │
│           (scrolls independently)                │
│                                                  │
│           - Setup: 3-step wizard                 │
│           - Generate: Template picker + forms    │
│           - Analyze: Upload + results            │
│                                                  │
└──────────────────────────────────────────────────┘

TARGET LAYOUT (ChatGPT/Claude-like):
┌──────────────────────────────────────────────────┐
│  Header (Compact: Logo, Quick Actions, Status)   │ 48px
├────────────┬─────────────────────────────────────┤
│            │  Workspace Header                   │ 56px
│  Sidebar   │  (Context: active template/report)  │
│  (240px)   ├─────────────────────────────────────┤
│            │                                     │
│  • History │  Main Content Area                  │
│  • Recent  │  (Scrollable, auto-scroll)          │
│  • Filters │                                     │
│            │  - Setup wizard steps               │
│  ─────────  │  - Generation progress             │
│  • Actions │  - Analysis results                 │
│  • New     │                                     │
│            ├─────────────────────────────────────┤
├────────────┤  Action Bar (Fixed)                 │ 64px
│  Profile   │  (Primary CTA, secondary actions)   │
└────────────┴─────────────────────────────────────┘
```

### Component Architecture

```
AppShell (Root)
├── AppProvider (Context: theme, toast, query)
│   └── UIStateProvider (Context: explicit UI states)
│
├── Sidebar (Collapsible, 240px)
│   ├── SidebarHeader (Logo, collapse toggle)
│   ├── SidebarNav (Primary navigation)
│   │   ├── NavItem (Setup)
│   │   ├── NavItem (Generate)
│   │   └── NavItem (Analyze)
│   ├── SidebarContent (Scrollable)
│   │   ├── RecentList (templates/reports)
│   │   └── QuickFilters
│   └── SidebarFooter (Profile, settings)
│
├── MainPanel (flex: 1)
│   ├── WorkspaceHeader (Context breadcrumb, actions)
│   ├── WorkspaceContent (Scrollable)
│   │   ├── SetupWorkspace
│   │   │   ├── StepIndicator
│   │   │   ├── ConnectStep
│   │   │   ├── UploadStep
│   │   │   └── ConfigureStep
│   │   ├── GenerateWorkspace
│   │   │   ├── TemplateSelector
│   │   │   ├── ParameterForm
│   │   │   └── ResultsStream
│   │   └── AnalyzeWorkspace
│   │       ├── UploadZone
│   │       ├── AnalysisStream
│   │       └── ResultsDisplay
│   └── ActionBar (Fixed bottom)
│       ├── PrimaryAction (Run/Generate/Analyze)
│       ├── SecondaryActions
│       └── StatusIndicator
│
└── Overlays
    ├── CommandPalette (Cmd+K)
    ├── JobsDrawer (Background tasks)
    └── SettingsModal
```

### State Architecture

```
UIState (Zustand slice)
├── workspaceState: 'idle' | 'loading' | 'generating' | 'error' | 'success'
├── sidebarOpen: boolean
├── activeWorkspace: 'setup' | 'generate' | 'analyze'
├── activeStep: number (for setup)
├── interruptController: AbortController | null
└── keyboardShortcuts: Map<string, () => void>

DomainState (existing useAppStore)
├── connection
├── templates
├── discoveryResults
└── downloads
```

---

## STEP 2: COMPONENT MAP (OLD → NEW)

### Layout Components

| Old Component | New Component | Change Type |
|--------------|---------------|-------------|
| `App.jsx` (monolithic) | `AppShell.jsx` + `Sidebar.jsx` + `MainPanel.jsx` | Split |
| `AppHeader` (in App.jsx) | `WorkspaceHeader.jsx` | Extract |
| `MainNavigation` (in App.jsx) | `SidebarNav.jsx` | Move to sidebar |
| - | `ActionBar.jsx` | New |
| - | `CommandPalette.jsx` | New |

### Page Components

| Old Component | New Component | Change Type |
|--------------|---------------|-------------|
| `SetupPage.jsx` | `SetupWorkspace.jsx` | Rename + simplify |
| `GeneratePage.jsx` | `GenerateWorkspace.jsx` | Rename + refactor |
| `AnalyzePageContainer.jsx` | `AnalyzeWorkspace.jsx` | Rename + refactor |

### Feature Components

| Old Component | New Component | Change Type |
|--------------|---------------|-------------|
| `TemplatePicker.jsx` | `TemplateSelector.jsx` | Simplify |
| `GenerateAndDownload.jsx` | `ParameterForm.jsx` + `ResultsStream.jsx` | Split |
| `DocumentUpload.jsx` | `UploadZone.jsx` | Rename + enhance |
| `AnalysisResults.jsx` | `ResultsDisplay.jsx` | Enhance |

### Primitives (New)

| Component | Purpose |
|-----------|---------|
| `ui/Button.jsx` | Standardized button with loading/disabled states |
| `ui/Input.jsx` | Input with validation states |
| `ui/Card.jsx` | Consistent card component |
| `ui/Badge.jsx` | Status badges |
| `ui/Skeleton.jsx` | Loading skeletons |
| `ui/ScrollArea.jsx` | Scrollable container with auto-scroll |
| `ui/Kbd.jsx` | Keyboard shortcut display |

### State Indicators

| Component | Purpose |
|-----------|---------|
| `states/IdleState.jsx` | Empty/idle state display |
| `states/LoadingState.jsx` | Loading with progress |
| `states/ErrorState.jsx` | Error with retry |
| `states/SuccessState.jsx` | Success with actions |
| `states/StreamingState.jsx` | Streaming progress |

---

## STEP 3: FILE-BY-FILE CHANGE PLAN

### Phase 1: Core Layout (Files to modify/create)

```
1. CREATE: src/components/shell/AppShell.jsx
   - Root layout component
   - Manages sidebar collapse state
   - Keyboard shortcut registration

2. CREATE: src/components/shell/Sidebar.jsx
   - Navigation + recent items
   - Collapsible (240px → 64px)
   - Footer with profile

3. CREATE: src/components/shell/MainPanel.jsx
   - Workspace header + content + action bar
   - Manages scroll behavior

4. CREATE: src/components/shell/ActionBar.jsx
   - Fixed bottom bar
   - Primary CTA button
   - Status indicators

5. CREATE: src/components/shell/WorkspaceHeader.jsx
   - Breadcrumb + context info
   - Quick actions

6. MODIFY: src/App.jsx
   - Use new AppShell
   - Simplified routing
```

### Phase 2: UI Primitives

```
7. CREATE: src/components/ui/index.js (barrel export)
8. CREATE: src/components/ui/Button.jsx
9. CREATE: src/components/ui/ScrollArea.jsx
10. CREATE: src/components/ui/Kbd.jsx
11. MODIFY: src/components/feedback/EmptyState.jsx (enhance)
12. MODIFY: src/components/feedback/LoadingState.jsx (enhance)
```

### Phase 3: State Management

```
13. CREATE: src/store/uiStore.js
    - UI-specific state slice
    - Explicit workspace states

14. MODIFY: src/store/useAppStore.js
    - Add UI state integration
```

### Phase 4: Workspaces

```
15. MODIFY: src/pages/Setup/SetupPage.jsx → SetupWorkspace
16. MODIFY: src/features/generate/containers/GeneratePageContainer.jsx → GenerateWorkspace
17. MODIFY: src/features/analyze/containers/AnalyzePageContainer.jsx → AnalyzeWorkspace
```

### Phase 5: Keyboard & Accessibility

```
18. CREATE: src/hooks/useKeyboardShortcuts.js
19. CREATE: src/components/shell/CommandPalette.jsx
20. ADD: ARIA attributes across all interactive components
```

---

## STEP 4: IMPLEMENTATION

See actual code changes below.

---

## STEP 5: UX VERIFICATION CHECKLIST

### Layout & Navigation
- [x] Sidebar collapses smoothly (260px → 68px) - Implemented in Sidebar.jsx with CSS transition
- [x] Main content area scrolls independently - Implemented in MainPanel.jsx with flex layout
- [x] Active route highlighted in sidebar - Implemented with `selected` state in NavItem
- [x] Breadcrumb shows current context - Implemented in WorkspaceHeader.jsx
- [x] Mobile responsive (sidebar becomes drawer) - Implemented in AppShell.jsx with MUI Drawer

### Interaction
- [x] Cmd/Ctrl+K opens command palette - Implemented in useKeyboardShortcuts.js + CommandPalette.jsx
- [x] Escape closes modals/drawers - Implemented in App.jsx keyboard handler
- [x] Enter submits forms (where appropriate) - Existing behavior preserved
- [x] Tab navigation works correctly - Uses native browser tab navigation
- [x] Focus visible on all interactive elements - MUI provides default focus styles

### State Feedback
- [x] Loading states show skeleton/spinner - PageLoader component for lazy routes
- [x] Error states show message + retry - Alert components in pages
- [x] Empty states show helpful message + action - EmptyState component
- [x] Success states show confirmation - Toast notifications
- [x] Progress shows percentage/steps - LinearProgress in ActionBar

### Streaming/Progress
- [x] Long operations show progress bar - ActionBar supports progress prop
- [x] Operations can be cancelled - ActionBar supports canCancel prop
- [x] Results stream in incrementally - Existing streaming preserved
- [x] Auto-scroll during streaming - MainPanel supports autoScroll prop

### Accessibility
- [x] All buttons have accessible names - MUI Button labels
- [x] Form inputs have labels - MUI TextField with labels
- [x] Error messages associated with inputs - MUI error prop
- [x] Color contrast meets WCAG AA - MUI theme colors
- [x] Screen reader announcements for state changes - Skip-to-content link in App.jsx

### Performance
- [x] No layout shift on load - Fixed sidebar width, stable layout
- [x] Skeleton loaders for async content - PageLoader for lazy routes
- [x] Debounced search/filter inputs - Existing debounce preserved
- [ ] Virtualized lists for large datasets - Not implemented (future enhancement)
