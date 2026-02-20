# NeuraReport UX Audit: Cognitive Load Elimination

**Audit Date:** 2026-01-21
**Auditor Roles:** Product Designer, UX Researcher, Frontend Architect, Accessibility & Usability Auditor

---

## STEP 1: FRONTEND SURFACE MAP (Exhaustive)

### 1.1 Pages

| Page | Route | Purpose |
|------|-------|---------|
| DashboardPage | `/`, `/dashboard` | Landing page with stats, quick actions, recent jobs |
| ConnectionsPage | `/connections` | Manage database connections |
| TemplatesPage | `/templates` | Manage report templates |
| ReportsPage | `/reports` | Generate reports with parameters |
| JobsPage | `/jobs` | View/manage running and completed jobs |
| SchedulesPage | `/schedules` | Configure scheduled report runs |
| AnalyzePage | `/analyze` | AI-powered data analysis |
| SettingsPage | `/settings` | Application settings |
| ActivityPage | `/activity` | Activity log |
| HistoryPage | `/history` | Report generation history |
| UsageStatsPage | `/stats` | Usage statistics |
| SetupWizard | `/setup/wizard` | 3-step template setup flow |
| TemplateEditorPage | `/templates/:id/edit` | Edit template mappings |

### 1.2 Modals & Dialogs

| Modal | Trigger Location | Purpose |
|-------|-----------------|---------|
| ConfirmModal (Delete Connection) | ConnectionsPage menu | Confirm connection deletion |
| ConfirmModal (Delete Template) | TemplatesPage menu | Confirm template deletion |
| ConfirmModal (Bulk Delete Templates) | TemplatesPage toolbar | Confirm bulk template deletion |
| ConfirmModal (Cancel Job) | JobsPage menu | Confirm job cancellation |
| ConfirmModal (Bulk Cancel Jobs) | JobsPage toolbar | Confirm bulk job cancellation |
| ConfirmModal (Bulk Delete Jobs) | JobsPage toolbar | Confirm bulk job deletion |
| Edit Template Details Dialog | TemplatesPage menu | Edit name, description, tags, status |
| Bulk Update Status Dialog | TemplatesPage toolbar | Change status of multiple templates |
| Bulk Add Tags Dialog | TemplatesPage toolbar | Add tags to multiple templates |
| Import Template Zip Dialog | TemplatesPage action | Import template from zip file |
| Job Details Dialog | JobsPage menu | View job details and download artifacts |
| Command Palette | Global Cmd+K | Quick navigation and commands |

### 1.3 Drawers

| Drawer | Location | Purpose |
|--------|----------|---------|
| ConnectionForm Drawer | ConnectionsPage | Create/edit database connection |
| ConnectionSchemaDrawer | ConnectionsPage menu | Inspect database schema |
| JobsPanel Drawer | Global | Slide-out panel showing active jobs |

### 1.4 Menus (Context Menus)

| Menu | Location | Items |
|------|----------|-------|
| Connection Row Menu | ConnectionsPage | Test Connection, Inspect Schema, Edit, Delete |
| Template Row Menu | TemplatesPage | Edit, Edit Details, Export, Duplicate, Delete |
| Job Row Menu | JobsPage | View Details, Download, Retry, Cancel |

### 1.5 Empty States

| Location | Current Title | Current Description |
|----------|--------------|---------------------|
| ConnectionsPage | "No connections yet" | "Add a database connection to start generating reports." |
| TemplatesPage | "No templates yet" | "Upload a PDF or Excel template to start generating reports." |
| JobsPage | "No jobs yet" | "Jobs will appear here when you generate reports." |
| DashboardPage Recent Jobs | (icon only) | "No jobs yet. Generate your first report to get started." |
| DashboardPage Top Templates | N/A | "No template usage data yet" |
| DashboardPage Favorites | N/A | "No favorites yet. Star templates or connections for quick access." |

### 1.6 Loading States

| Location | Type |
|----------|------|
| PageLoader | CircularProgress + "Loading..." text |
| DataTable | Skeleton rows |
| DashboardPage | LinearProgress bar |
| ReportsPage Discovery | LinearProgress bar |
| ReportsPage Generation | LinearProgress + "Generating report..." |
| JobsPage Refresh | IconButton with CircularProgress |

### 1.7 Error States

| Location | Current Implementation |
|----------|----------------------|
| ConnectionForm | Alert component with inline error |
| ReportsPage | Alert component with close button |
| JobsPage Job Details | Alert component showing error message |
| Toast notifications | Various error toasts |

### 1.8 Form Fields (All Inputs)

| Page | Field | Type | Label |
|------|-------|------|-------|
| ConnectionForm | name | TextField | "Connection Name" |
| ConnectionForm | db_type | Select | "Database Type" |
| ConnectionForm | host | TextField | "Host" |
| ConnectionForm | port | TextField (number) | "Port" |
| ConnectionForm | database | TextField | "Database Name" / "Database Path" |
| ConnectionForm | username | TextField | "Username" |
| ConnectionForm | password | TextField (password) | "Password" |
| ConnectionForm | ssl | Switch | "Use SSL" |
| ReportsPage | template | Select | "Template" |
| ReportsPage | startDate | TextField (date) | "Start Date" |
| ReportsPage | endDate | TextField (date) | "End Date" |
| ReportsPage | keyValues | Select (dynamic) | (field name) |
| Edit Template Details | name | TextField | "Name" |
| Edit Template Details | description | TextField (multiline) | "Description" |
| Edit Template Details | tags | TextField | "Tags" |
| Edit Template Details | status | Select | "Status" |
| Import Template | file | file input | "Choose zip file" |
| Import Template | name | TextField | "Template Name (optional)" |
| Bulk Update Status | status | Select | "Status" |
| Bulk Add Tags | tags | TextField | "Tags" |

### 1.9 Buttons (All Actions)

| Location | Label | Current Copy |
|----------|-------|--------------|
| DashboardPage | Primary CTA | "New Report" |
| DashboardPage | Refresh | (icon only) |
| ConnectionsPage | Add | "Add Connection" |
| ConnectionsPage Menu | Test | "Test Connection" |
| ConnectionsPage Menu | Schema | "Inspect Schema" |
| ConnectionsPage Menu | Edit | "Edit" |
| ConnectionsPage Menu | Delete | "Delete" |
| ConnectionForm | Submit | "Add Connection" / "Update Connection" |
| ConnectionForm | Cancel | "Cancel" |
| TemplatesPage | Add | "Upload Template" |
| TemplatesPage | Import | "Import Zip" |
| TemplatesPage Menu | Edit | "Edit" |
| TemplatesPage Menu | Details | "Edit Details" |
| TemplatesPage Menu | Export | "Export" |
| TemplatesPage Menu | Duplicate | "Duplicate" |
| TemplatesPage Menu | Delete | "Delete" |
| TemplatesPage Bulk | Status | "Update Status" |
| TemplatesPage Bulk | Tags | "Add Tags" |
| ReportsPage | Discover | "Discover" |
| ReportsPage | Schedule | "Schedule" |
| ReportsPage | Generate | "Generate Report" |
| ReportsPage Batches | Select All | "Select all" |
| ReportsPage Batches | Clear | "Clear" |
| JobsPage | Refresh | "Refresh" |
| JobsPage Menu | Details | "View Details" |
| JobsPage Menu | Download | "Download" |
| JobsPage Menu | Retry | "Retry" |
| JobsPage Menu | Cancel | "Cancel" |
| All Dialogs | Confirm (destructive) | "Delete" / "Cancel Job" |
| All Dialogs | Cancel | "Cancel" |

### 1.10 Table Columns

| Table | Columns |
|-------|---------|
| Connections | Name, Type, Status, Latency, Last Connected |
| Templates | Template, Type, Status, Fields, Tags, Created, Last Run, Updated |
| Jobs | Job ID, Type, Template, Status, Progress, Started, Completed |

### 1.11 Filters

| Table | Filters |
|-------|---------|
| Connections | Status (Connected, Disconnected, Error), Type (PostgreSQL, MySQL, SQL Server, SQLite) |
| Templates | Type (PDF, Excel), Status (Approved, Pending, Draft, Archived), Tags (dynamic) |
| Jobs | Status (Pending, Running, Completed, Failed, Cancelled), Type (Report, Batch, Schedule) |

### 1.12 Navigation Elements

| Element | Items |
|---------|-------|
| Sidebar | Dashboard, Connections, Templates, Jobs, Reports, Schedules, Analyze, Settings, Activity, History, Usage Stats |
| TopNav | Menu toggle, Connection indicator |
| Quick Actions (Dashboard) | Manage Connections, View Templates, Generate Report, Manage Schedules |

---

## STEP 2: PAGE-BY-PAGE DECONSTRUCTION

### 2.1 Dashboard Page

#### Element: Page Title "Welcome to NeuraReport"
1. **Does a first-time user understand what this is?** No - "NeuraReport" doesn't explain what the app does
2. **Is jargon-free?** Yes
3. **Is it obvious what to do next?** Somewhat - "New Report" button exists but user doesn't know prerequisites
4. **What's the worst outcome?** User clicks "New Report" without database connection
5. **What assumption?** User knows they need database + template first
6. **Can outcome be auto-detected?** Yes - check if connections/templates exist
7. **Can choice be inferred?** N/A
8. **Is there feedback?** No immediate feedback on what's missing
9. **Destructive? Recovery?** No
10. **Error handling?** Clicking "New Report" goes to wizard which handles missing state

#### Element: Stat Card "Connections"
1. **Understand?** Somewhat - "connections" is database jargon
2. **Jargon-free?** No - "connections" is technical
3. **Obvious next step?** Yes - clickable to manage
4. **Worst outcome?** None
5. **Assumption?** User knows "connection" = database link
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Shows count
9. **Destructive?** No
10. **Error?** N/A

#### Element: Stat Card "Templates"
1. **Understand?** Partially - "templates" is vague
2. **Jargon-free?** Somewhat - template is common but context unclear
3. **Obvious next step?** Clickable
4. **Worst outcome?** None
5. **Assumption?** User knows what templates are in this context
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Shows PDF/Excel breakdown
9. **Destructive?** No
10. **Error?** N/A

#### Element: "Jobs Today" Stat
1. **Understand?** No - "jobs" is backend terminology
2. **Jargon-free?** No
3. **Obvious?** No - what's a job?
4. **Worst outcome?** Confusion
5. **Assumption?** User understands async job processing
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Count shown
9. **Destructive?** No
10. **Error?** N/A

#### Element: Quick Action "Generate Report"
1. **Understand?** Yes - clear action
2. **Jargon-free?** Yes
3. **Obvious?** Yes
4. **Worst outcome?** Goes to reports page without data
5. **Assumption?** User has setup complete
6. **Auto-detect?** Yes - could disable if no templates
7. **Infer?** N/A
8. **Feedback?** Navigation occurs
9. **Destructive?** No
10. **Error?** Shows warning on reports page if no connection

### 2.2 Connections Page

#### Element: Page Title "Connections"
1. **Understand?** No - "connection" to what?
2. **Jargon-free?** No
3. **Obvious?** No
4. **Worst outcome?** User doesn't understand page purpose
5. **Assumption?** User knows database connections
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Subtitle helps: "Manage your database connections"
9. **Destructive?** No
10. **Error?** N/A

#### Element: "Add Connection" Button
1. **Understand?** Partially
2. **Jargon-free?** No
3. **Obvious?** Yes - primary action
4. **Worst outcome?** User doesn't know what info needed
5. **Assumption?** User has database credentials
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Opens drawer
9. **Destructive?** No
10. **Error?** Form validates

#### Element: Connection Form "Database Type" Select
1. **Understand?** Partially - shows technical DB names
2. **Jargon-free?** No - PostgreSQL, MySQL, etc. are technical
3. **Obvious?** Not for non-technical users
4. **Worst outcome?** User picks wrong type
5. **Assumption?** User knows their database type
6. **Auto-detect?** Could potentially auto-detect from connection string
7. **Infer?** N/A
8. **Feedback?** Selection shown
9. **Destructive?** No
10. **Error?** Wrong type = connection failure

#### Element: Connection Form "Host" Field
1. **Understand?** No - "host" is networking jargon
2. **Jargon-free?** No
3. **Obvious?** No
4. **Worst outcome?** Wrong server address
5. **Assumption?** User knows server hostname/IP
6. **Auto-detect?** No
7. **Infer?** Default "localhost" helps for local setups
8. **Feedback?** Placeholder shown
9. **Destructive?** No
10. **Error?** Connection test fails

#### Element: Connection Form "Port" Field
1. **Understand?** No - technical networking term
2. **Jargon-free?** No
3. **Obvious?** No
4. **Worst outcome?** Wrong port
5. **Assumption?** User knows port numbers
6. **Auto-detect?** Yes - defaults based on DB type (good!)
7. **Infer?** Yes - auto-sets on DB type change (good!)
8. **Feedback?** Number shown
9. **Destructive?** No
10. **Error?** Connection fails

#### Element: Empty State "No connections yet"
1. **Understand?** Partially
2. **Jargon-free?** No - "connections"
3. **Obvious?** Yes - clear CTA to add
4. **Worst outcome?** User doesn't know what to add
5. **Assumption?** User has database access
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Description explains purpose
9. **Destructive?** No
10. **Error?** N/A

#### Element: Menu Item "Inspect Schema"
1. **Understand?** No - "schema" is database jargon
2. **Jargon-free?** No
3. **Obvious?** No
4. **Worst outcome?** User confused by output
5. **Assumption?** User understands database schemas
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Opens drawer
9. **Destructive?** No
10. **Error?** N/A

### 2.3 Templates Page

#### Element: Page Title "Templates"
1. **Understand?** Vaguely - templates of what?
2. **Jargon-free?** Somewhat
3. **Obvious?** No - purpose unclear
4. **Worst outcome?** User doesn't understand relationship to reports
5. **Assumption?** User knows template = report layout file
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Subtitle: "Manage your report templates"
9. **Destructive?** No
10. **Error?** N/A

#### Element: "Upload Template" Button
1. **Understand?** Partially - upload what format?
2. **Jargon-free?** Yes
3. **Obvious?** Yes
4. **Worst outcome?** User uploads wrong file type
5. **Assumption?** User has PDF/Excel template files
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Goes to wizard
9. **Destructive?** No
10. **Error?** Wizard validates file

#### Element: Column "Fields"
1. **Understand?** No - fields of what?
2. **Jargon-free?** Somewhat
3. **Obvious?** No
4. **Worst outcome?** Confusion
5. **Assumption?** User knows about token/field mapping
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Number shown
9. **Destructive?** No
10. **Error?** N/A

#### Element: Status "Approved"
1. **Understand?** Partially - approved by whom?
2. **Jargon-free?** Yes
3. **Obvious?** No - workflow unclear
4. **Worst outcome?** User doesn't know if template is usable
5. **Assumption?** User understands approval workflow
6. **Auto-detect?** Could default to approved for single-user
7. **Infer?** N/A
8. **Feedback?** Chip color indicates state
9. **Destructive?** No
10. **Error?** N/A

### 2.4 Reports Page

#### Element: Alert "Please connect to a database first"
1. **Understand?** Yes (good!)
2. **Jargon-free?** Somewhat - "database" is technical
3. **Obvious?** Yes - tells user what's wrong
4. **Worst outcome?** User doesn't know how to connect
5. **Assumption?** User can find connections page
6. **Auto-detect?** Good - auto-detects missing connection!
7. **Infer?** N/A
8. **Feedback?** Warning alert shown
9. **Destructive?** N/A
10. **Error?** This IS the error feedback (good)

#### Element: "Discover Batches" Button
1. **Understand?** No - what are batches?
2. **Jargon-free?** No - "batches" is processing jargon
3. **Obvious?** No
4. **Worst outcome?** User skips important step
5. **Assumption?** User knows batch = grouping of data
6. **Auto-detect?** Could auto-discover
7. **Infer?** Yes - could run automatically
8. **Feedback?** Shows loading, then results
9. **Destructive?** No
10. **Error?** Toast on failure

#### Element: "Filter Parameters" Section
1. **Understand?** Partially
2. **Jargon-free?** Somewhat
3. **Obvious?** No - appears conditionally
4. **Worst outcome?** User doesn't filter, gets too much data
5. **Assumption?** User knows available filter values
6. **Auto-detect?** Yes - fetches options from DB (good!)
7. **Infer?** N/A
8. **Feedback?** Dropdown populated dynamically
9. **Destructive?** No
10. **Error?** Console error only (bad)

#### Element: "Generate Report" Button
1. **Understand?** Yes
2. **Jargon-free?** Yes
3. **Obvious?** Yes - primary action
4. **Worst outcome?** Generates with wrong parameters
5. **Assumption?** User configured correctly
6. **Auto-detect?** Validates required fields
7. **Infer?** N/A
8. **Feedback?** Progress shown, then success
9. **Destructive?** No - creates job
10. **Error?** Toast + inline alert

### 2.5 Jobs Page

#### Element: Page Title "Jobs"
1. **Understand?** No - what kind of jobs?
2. **Jargon-free?** No - background processing term
3. **Obvious?** No
4. **Worst outcome?** User confused
5. **Assumption?** User knows async job processing
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Subtitle shows active count
9. **Destructive?** No
10. **Error?** N/A

#### Element: Column "Job ID"
1. **Understand?** Partially - technical identifier
2. **Jargon-free?** No
3. **Obvious?** No - why show truncated ID?
4. **Worst outcome?** None
5. **Assumption?** User needs ID for debugging
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Monospace font
9. **Destructive?** No
10. **Error?** N/A

#### Element: Status "Pending/Running/Completed/Failed"
1. **Understand?** Yes - familiar terms
2. **Jargon-free?** Yes
3. **Obvious?** Yes
4. **Worst outcome?** None
5. **Assumption?** None
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Color-coded chips (good!)
9. **Destructive?** No
10. **Error?** Failed status shown clearly

### 2.6 Setup Wizard

#### Element: Step 1 "Connect Database"
1. **Understand?** Partially - "connect" is vague
2. **Jargon-free?** No - "database" is technical
3. **Obvious?** Yes - first step is clear
4. **Worst outcome?** User can't proceed without credentials
5. **Assumption?** User has DB credentials ready
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** Step indicator shows progress
9. **Destructive?** No
10. **Error?** Connection test shows result

#### Element: Step 2 "Upload Template"
1. **Understand?** Partially - upload what?
2. **Jargon-free?** Somewhat
3. **Obvious?** Yes - file upload
4. **Worst outcome?** Wrong file type uploaded
5. **Assumption?** User has correct file format
6. **Auto-detect?** N/A
7. **Infer?** N/A
8. **Feedback?** File name shown after upload
9. **Destructive?** No
10. **Error?** File validation

#### Element: Step 3 "Configure Mapping"
1. **Understand?** No - mapping what to what?
2. **Jargon-free?** No - "mapping" is technical
3. **Obvious?** No
4. **Worst outcome?** Incorrect mappings = wrong data in report
5. **Assumption?** User understands data mapping
6. **Auto-detect?** Could use AI to suggest
7. **Infer?** Yes - smart defaults possible
8. **Feedback?** Shows fields
9. **Destructive?** No
10. **Error?** Validation on complete

---

## STEP 3: LAYMAN TRANSLATION RULE

### 3.1 Page Titles & Headers

| Current | Problem | New Copy |
|---------|---------|----------|
| "Welcome to NeuraReport" | Brand name doesn't explain purpose | "Your Reports Dashboard" |
| "Connections" | Database jargon | "Your Data Sources" |
| "Manage your database connections" | Technical | "Where your data lives" |
| "Templates" | Vague | "Report Designs" |
| "Manage your report templates" | Unclear relationship | "Your saved report layouts" |
| "Generate Reports" | Passive | "Create a Report" |
| "Jobs" | Backend terminology | "Report Progress" |
| "All jobs completed" | Jargon | "All reports finished" |
| "Schedules" | Vague | "Automatic Reports" |
| "Analyze" | Vague | "Ask Questions About Your Data" |

### 3.2 Stat Cards (Dashboard)

| Current | Problem | New Copy |
|---------|---------|----------|
| "Connections" | Jargon | "Data Sources" |
| "X active" | What's active? | "X ready to use" |
| "Templates" | Vague | "Report Designs" |
| "X PDF, Y Excel" | File types as feature | "X document, Y spreadsheet" |
| "Jobs Today" | What's a job? | "Reports Created Today" |
| "X this week" | Good | Keep as is |
| "Success Rate" | Good | Keep as is |
| "X completed" | Good | Keep as is |
| "Schedules" | Vague | "Automatic Reports" |
| "X active" | What does active mean? | "X running automatically" |

### 3.3 Quick Actions

| Current | Problem | New Copy |
|---------|---------|----------|
| "Manage Connections" | Jargon | "Set Up Data Source" |
| "View Templates" | Passive | "View Report Designs" |
| "Generate Report" | Technical verb | "Create a Report" |
| "Manage Schedules" | Technical | "Set Up Automatic Reports" |

### 3.4 Buttons

| Current | Problem | New Copy |
|---------|---------|----------|
| "New Report" | Good | Keep as is |
| "Add Connection" | Jargon | "Add Data Source" |
| "Upload Template" | Vague | "Add Report Design" |
| "Import Zip" | Technical | "Import from File" |
| "Test Connection" | Technical | "Check if it works" |
| "Inspect Schema" | Very technical | "View Tables & Columns" |
| "Edit Details" | Vague | "Change Name & Settings" |
| "Export" | Good | Keep as is |
| "Duplicate" | Good | Keep as is |
| "Generate Report" | Good | "Create Report" |
| "Discover" | Cryptic | "Find Available Data" |
| "Discover Batches" | Very cryptic | "Find Data Groups" |
| "Select all" / "Clear" | Good | Keep as is |
| "Schedule" | Vague | "Run Automatically" |
| "View Details" | Good | Keep as is |
| "Retry" | Good | "Try Again" |
| "Cancel" | Good | "Stop" (for jobs) |
| "Refresh" | Good | Keep as is |

### 3.5 Form Labels

| Current | Problem | New Copy |
|---------|---------|----------|
| "Connection Name" | Jargon | "Name this data source" |
| "Database Type" | Technical | "What kind of database?" |
| "Host" | Networking jargon | "Server address" |
| "Port" | Technical | "Port number (usually automatic)" |
| "Database Name" | OK but could clarify | "Database name on the server" |
| "Database Path" (SQLite) | OK | "File location" |
| "Username" | Good | Keep as is |
| "Password" | Good | Keep as is |
| "Use SSL" | Technical | "Use secure connection (recommended)" |
| "Advanced Settings" | Good | Keep as is |
| "Template" | Vague in context | "Report design to use" |
| "Start Date" | Good | Keep as is |
| "End Date" | Good | Keep as is |
| "Filter Parameters" | Technical | "Narrow down your data" |
| "Tags" | Good | Keep as is |
| "Status" | Vague | "Availability" |

### 3.6 Table Columns

| Current | Problem | New Copy |
|---------|---------|----------|
| "Name" | Good | Keep as is |
| "Type" | Vague | "Format" (for templates) or "Database" (for connections) |
| "Status" | Vague | "Ready?" or "State" |
| "Latency" | Technical | "Speed" |
| "Last Connected" | OK | "Last used" |
| "Fields" | Cryptic | "Data points" |
| "Job ID" | Very technical | "Reference #" |
| "Progress" | Good | Keep as is |
| "Started" | Good | Keep as is |
| "Completed" | Good | "Finished" |

### 3.7 Empty States

| Current | Problem | New Copy |
|---------|---------|----------|
| "No connections yet" | Jargon | "No data sources added yet" |
| "Add a database connection to start generating reports." | Technical | "Connect to where your data lives, like a database or spreadsheet." |
| "No templates yet" | Vague | "No report designs yet" |
| "Upload a PDF or Excel template to start generating reports." | Better but still technical | "Add a document or spreadsheet that shows how your reports should look." |
| "No jobs yet" | Jargon | "No reports in progress" |
| "Jobs will appear here when you generate reports." | Technical | "When you create reports, you'll see their progress here." |
| "No template usage data yet" | Technical | "You haven't created any reports yet" |
| "No favorites yet. Star templates or connections for quick access." | OK | "Star items you use often for quick access" |

### 3.8 Error Messages

| Current | Problem | New Copy |
|---------|---------|----------|
| "Failed to delete connection" | Generic | "Couldn't remove this data source. It might be in use by a report." |
| "Connection test failed" | Generic | "Couldn't connect. Check your server address and credentials." |
| "Failed to save connection" | Generic | "Couldn't save. Please check all fields are filled correctly." |
| "Failed to load templates" | Generic | "Couldn't load your report designs. Please refresh the page." |
| "Failed to generate report" | Generic | "Something went wrong creating your report. Please try again." |
| "Select at least one batch to run" | Jargon | "Select at least one data group to include in your report." |
| "Please connect to a database first to generate reports." | OK | "First, add a data source so we know where to get your data." |

### 3.9 Success Messages (Toasts)

| Current | Problem | New Copy |
|---------|---------|----------|
| "Connection deleted" | OK but passive | "Data source removed" |
| "Connection added" | Passive | "Data source added successfully!" |
| "Connection updated" | OK | "Changes saved" |
| "Template deleted" | OK | "Report design removed" |
| "Template duplicated as '...'" | Good | Keep as is |
| "Report generation started!" | Good | "Creating your report..." |
| "Jobs refreshed" | OK | "Updated" |
| "Job cancelled" | OK | "Report stopped" |

### 3.10 Confirmation Dialogs

| Current | Problem | New Copy |
|---------|---------|----------|
| "Delete Connection" | OK | "Remove Data Source" |
| "Are you sure you want to delete '...'? This action cannot be undone." | Good | Keep as is, but change "delete" to "remove" |
| "Delete Template" | OK | "Remove Report Design" |
| "Cancel Job" | Jargon | "Stop this report?" |
| "Are you sure you want to cancel this job? This action cannot be undone." | Jargon | "Stop creating this report? You can start it again later." |

### 3.11 Status Labels

| Current | Problem | New Copy |
|---------|---------|----------|
| "connected" | OK | "Ready" |
| "disconnected" | OK | "Not connected" |
| "error" | OK | "Problem" |
| "approved" | Confusing | "Ready to use" |
| "pending" | OK | "Waiting" |
| "draft" | OK | "Not finished" |
| "archived" | OK | "Hidden" |
| "running" | OK | "Working..." |
| "completed" | OK | "Done" |
| "failed" | OK but harsh | "Problem occurred" |
| "cancelled" | OK | "Stopped" |

---

## STEP 4: ERROR & FAILURE FIRST DESIGN

### 4.1 Connection Actions

#### Add Connection
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Invalid server address | Toast on test | Inline validation: "We couldn't find a server at this address. Double-check the spelling." |
| Wrong credentials | Toast on test | Inline: "The username or password doesn't match. Check with your database administrator." |
| Wrong port | Toast on test | Inline: "Couldn't connect on this port. The default for [DB type] is [port]." |
| Wrong database name | Toast on test | Inline: "No database called '[name]' was found on this server." |
| Network timeout | Toast on test | Inline: "Connection timed out. The server might be offline or behind a firewall." |
| SSL required | Toast on test | Inline: "This server requires a secure connection. Enable 'Use secure connection' above." |

**Proposed Error State UX:**
- Test connection BEFORE allowing save
- Show specific, actionable error messages inline below the failing field
- Provide "What's this?" links with expanded help
- Show "Common issues" collapsible section with troubleshooting

#### Delete Connection
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Connection in use by template | Generic toast | Modal: "This data source is used by [X] report designs. Remove it from those first, or they won't work." with list of affected templates |
| Network error during delete | Generic toast | Toast with retry: "Couldn't remove. Tap to try again." |

### 4.2 Template Actions

#### Upload Template
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Wrong file type | Unknown | "This file type isn't supported. Please upload a PDF or Excel file (.pdf, .xlsx, .xls)" |
| File too large | Unknown | "This file is too large (max 10MB). Try compressing images in your document." |
| Corrupted file | Unknown | "We couldn't read this file. It might be corrupted. Try re-exporting it." |
| No tokens found | Unknown | "We didn't find any fillable fields (like {{name}}) in this document. Make sure your template has placeholders." |

#### Delete Template
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Template has scheduled reports | Generic toast | Modal: "This design has [X] automatic reports set up. Removing it will cancel those schedules." with list |
| Template has active jobs | Generic toast | Modal: "A report using this design is currently being created. Wait for it to finish or stop it first." |

### 4.3 Report Generation

#### Generate Report
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| No connection selected | Alert shown | Keep but rephrase: "Select a data source first. You can add one in Settings > Data Sources." with link |
| No template selected | Validation | "Select a report design first." |
| Connection offline | Toast | Inline error: "Couldn't connect to [connection name]. Check if the server is running." with "Test connection" button |
| Date range invalid | Validation | "End date must be after start date." |
| No data in date range | Toast | Result panel: "No data found for these dates. Try a wider date range." |
| Query timeout | Toast | "This is taking too long. Try a smaller date range or contact support." |
| Out of memory | Generic error | "This report is too large. Try adding filters or a smaller date range." |

### 4.4 Job Management

#### Cancel Job
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Job already completed | Unknown | Toast: "This report already finished! Check your downloads." |
| Job already failed | Unknown | Toast: "This report already stopped due to an error." |
| Network error | Generic toast | Toast with retry: "Couldn't stop the report. Tap to try again." |

#### Retry Job
| What can fail | Current handling | Required handling |
|---------------|------------------|-------------------|
| Original parameters invalid | Unknown | Modal: "The original settings for this report are no longer valid. Create a new report instead." |
| Connection no longer exists | Unknown | Modal: "The data source '[name]' used for this report was removed. Choose a different data source." |
| Template no longer exists | Unknown | Modal: "The report design used for this report was removed." |

### 4.5 Recovery Paths

Every error should have a clear recovery action:

| Error category | Recovery pattern |
|----------------|------------------|
| Network errors | "Retry" button + "Check connection" link |
| Validation errors | Highlight field + clear instruction |
| Permission errors | Link to help docs or admin contact |
| Not found errors | Link to recreate or choose alternative |
| Timeout errors | Suggest breaking into smaller chunks |
| Unknown errors | "Report this issue" link + error code |

---

## STEP 5: DECISION MINIMIZATION

### 5.1 Decisions That Can Be REMOVED

| Decision | Current state | Recommendation |
|----------|---------------|----------------|
| Template status (approved/pending/draft/archived) | User must choose | Auto-set to "ready" for single users. Only show status workflow in team mode. |
| Connection SSL toggle | User must choose | Default to ON, only show toggle in advanced settings |
| Port number | User must enter | Auto-detect from database type (already done - keep) |
| Template tags | User must enter | Remove entirely unless user opts in. Tags are power-user feature. |
| Output format selection (PDF/DOCX/XLSX) | Multiple checkboxes | Default to PDF only. Add "Also create Word doc" as secondary option. |
| Batch selection | User must select from list | Auto-select all by default. "Select specific data groups" as toggle to show picker. |

### 5.2 Decisions That Can Be AUTO-SELECTED

| Decision | Current state | Smart default |
|----------|---------------|---------------|
| Template to use | User picks from dropdown | Pre-select most recently used. Show "Recommended: [template]" based on usage |
| Date range | User enters both dates | Default to "Last month" preset with quick buttons: Today, This Week, This Month, Last Month, Custom |
| Connection to use | Implicit (active connection) | Good - keep showing "Using: [connection name]" indicator |
| Filter parameters | User selects from each dropdown | Default to "All" which is already done. Good. |

### 5.3 Decisions That Can Be INFERRED

| Decision | Signal | Inference |
|----------|--------|-----------|
| Which template to use | User clicked "Create Report" from a template row | Pre-select that template |
| Date range | Report has "monthly" in name or tags | Default to "This Month" range |
| Database type | Connection string format | Parse and auto-detect type |
| Template type | File extension on upload | Set PDF/Excel automatically (already done) |

### 5.4 Decisions That Can Be POSTPONED

| Decision | Current timing | Better timing |
|----------|----------------|---------------|
| Template description | During upload | After first successful report |
| Template tags | During upload/edit | Never prompt; let user add if wanted |
| Schedule configuration | Separate page | Offer after report completes: "Want to run this automatically?" |
| Advanced connection settings | Visible in form | Hide under "Advanced" (already done - keep) |

### 5.5 Proposed Simplified Flows

#### Current "Create Report" Flow (7 decisions):
1. Go to Reports page
2. Select template
3. (Implicitly use active connection)
4. Enter start date
5. Enter end date
6. Optionally set filter parameters
7. Optionally discover and select batches
8. Click Generate

#### Simplified "Create Report" Flow (2-3 decisions):
1. Click "Create Report" from anywhere
2. See pre-selected template (most recent or from context) + last-used date range
3. Click "Create" OR adjust dates/template
4. Done

**Implementation:**
- One-click report from template list
- Smart date range presets (not two date pickers)
- Skip batch discovery unless data exceeds threshold
- Filter parameters only shown if multiple distinct values exist

### 5.6 Wizard Flow Simplification

#### Current Setup Wizard (3 steps, many fields):
1. **Connect Database**
   - Name
   - Type
   - Host
   - Port
   - Database
   - Username
   - Password
   - SSL

2. **Upload Template**
   - File upload
   - Name (optional)

3. **Configure Mapping**
   - Map each token to column

#### Proposed Setup Wizard (3 steps, minimal fields):

**Step 1: "Where's your data?"**
- Big buttons: "Use Demo Data" (for exploration) | "Connect My Database"
- If database: Simple preset buttons for common setups (Supabase, Railway, Render, Local)
- Connection string paste option: "Have a connection URL? Paste it here"
- Only ask for name + password for hosted options

**Step 2: "What should your report look like?"**
- Big buttons: "Use a Sample" (pre-built templates) | "Upload My Own"
- If sample: Show 3-4 common report types with previews
- If own: Simple drag-drop zone with clear file type guidance

**Step 3: "We found these fields"**
- Show auto-detected mapping preview
- AI suggests matches: "{{customer_name}} → customers.name ✓"
- Single "Looks good" button for happy path
- "Let me adjust" link for manual mapping

---

## STEP 6: MISSING FEATURES (Required Additions)

### 6.1 Onboarding & Guidance

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Interactive product tour** | First-time users don't know where to start | P0 |
| **Empty state CTAs with context** | "No connections" should show demo option | P0 |
| **Progress checklist** | "Setup: 1 of 3 complete" persistent indicator | P1 |
| **Contextual help tooltips** | "?" icons with explanations on technical fields | P1 |
| **Sample data mode** | Let users explore without real database | P0 |

### 6.2 Error Prevention

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Connection test on form blur** | Test as user fills in, not only on submit | P1 |
| **Template validation preview** | Show found tokens before completing upload | P0 |
| **Mapping suggestions with AI** | Auto-map tokens to likely columns | P1 |
| **"Undo" for destructive actions** | Toast with "Undo" button for 5 seconds after delete | P1 |

### 6.3 Progress & Status Communication

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Step-by-step progress for report generation** | "Fetching data... (1/4)" not just percentage | P0 |
| **Real-time job updates** | Push notifications / live updates (partially exists) | P1 |
| **Email notification on complete** | User can leave page and get notified | P2 |
| **Estimated time remaining** | "About 2 minutes left" on long jobs | P2 |

### 6.4 Recovery & Support

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Inline error recovery actions** | "Fix this" buttons, not just error messages | P0 |
| **"Report a problem" from error states** | Pre-filled bug report with context | P2 |
| **Connection troubleshooter wizard** | Step-by-step "Can't connect? Let's fix it" | P1 |
| **Export error logs** | For technical users to debug | P2 |

### 6.5 Accessibility

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Keyboard navigation for all actions** | Tab through menus, Enter to confirm | P0 |
| **Screen reader announcements** | ARIA live regions for status changes | P1 |
| **High contrast mode** | Dark theme exists but need true high contrast option | P2 |
| **Focus management on modal open/close** | Focus trap and return focus on close | P0 |

### 6.6 Confirmation & Assurance

| Feature | Justification | Priority |
|---------|---------------|----------|
| **Success celebration** | Brief animation on first successful report | P2 |
| **"What just happened" summary** | After actions: "Your report is being created. It usually takes 1-2 minutes." | P0 |
| **Pre-submission preview** | "You're about to create a report using Template X with data from Jan 1-31" | P1 |

---

## STEP 7: FINAL OUTPUT SPECIFICATION

### 7.1 Page-Level Specifications

---

#### PAGE: Dashboard (`/`)

**Title:** "Your Reports Dashboard"
**Subtitle:** "Create reports from your data in minutes"

**First-time user view (no data):**
```
┌─────────────────────────────────────────────────────────┐
│  Your Reports Dashboard                                 │
│  Create reports from your data in minutes               │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  🎉 Welcome! Let's create your first report.    │   │
│  │                                                  │   │
│  │  ○ Add a data source (where your data lives)    │   │
│  │  ○ Add a report design (how it should look)     │   │
│  │  ○ Create your first report                     │   │
│  │                                                  │   │
│  │  [Get Started]  [Try with Demo Data]            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Stat cards (with data):**
| Position | Title | Subtitle pattern |
|----------|-------|------------------|
| 1 | "Data Sources" | "X ready to use" |
| 2 | "Report Designs" | "X document, Y spreadsheet" |
| 3 | "Created Today" | "X this week" |
| 4 | "Success Rate" | "X finished successfully" |
| 5 | "Automatic Reports" | "X running on schedule" |

**Quick actions:**
- "Add Data Source" (icon: database)
- "View Report Designs" (icon: document)
- "Create a Report" (icon: play)
- "Set Up Automatic Reports" (icon: clock)

---

#### PAGE: Connections (`/connections`)

**Title:** "Data Sources"
**Subtitle:** "Where your data lives"

**Empty state:**
```
┌─────────────────────────────────────────────────────────┐
│           [Database Icon]                               │
│                                                         │
│     No data sources added yet                           │
│                                                         │
│     Connect to your database, spreadsheet, or other     │
│     data source so we know where to get your data.      │
│                                                         │
│     [Add Data Source]  or  [Use Demo Data]              │
└─────────────────────────────────────────────────────────┘
```

**Primary action:** "Add Data Source"

**Table columns:**
| Column | Header text |
|--------|-------------|
| Name | "Name" |
| Type | "Database" |
| Status | "Status" (show as "Ready" / "Problem" / "Not connected") |
| Speed | "Response time" |
| Last used | "Last used" |

**Row menu items:**
- "Check Connection" (replaces "Test Connection")
- "View Tables & Columns" (replaces "Inspect Schema")
- "Edit"
- "Remove" (replaces "Delete")

**Connection form - Field labels:**
| Field | Label | Placeholder | Help text |
|-------|-------|-------------|-----------|
| name | "What should we call this?" | "e.g., Production Database" | - |
| db_type | "What kind of database?" | - | "Not sure? Ask your administrator" |
| host | "Server address" | "e.g., db.example.com" | "The URL or IP address of your database server" |
| port | "Port number" | (auto-filled) | "Usually you don't need to change this" |
| database | "Database name" | "e.g., my_database" | "The name of the specific database on the server" |
| username | "Username" | "e.g., admin" | - |
| password | "Password" | "Enter password" | "This will be stored securely" |
| ssl | "Use secure connection" | - | "Recommended for production databases" |

**Form submit button:** "Save & Test Connection"

**Delete confirmation:**
```
┌─────────────────────────────────────────────────────────┐
│  Remove "[Name]"?                                       │
│                                                         │
│  [Warning Icon]                                         │
│                                                         │
│  This will remove access to this data source.           │
│  Any reports using it won't work until you              │
│  connect it again.                                      │
│                                                         │
│  [Cancel]  [Remove]                                     │
└─────────────────────────────────────────────────────────┘
```

---

#### PAGE: Templates (`/templates`)

**Title:** "Report Designs"
**Subtitle:** "How your reports look"

**Empty state:**
```
┌─────────────────────────────────────────────────────────┐
│           [Document Icon]                               │
│                                                         │
│     No report designs yet                               │
│                                                         │
│     Add a PDF or spreadsheet that shows how your        │
│     reports should look. We'll fill in the data         │
│     automatically.                                      │
│                                                         │
│     [Add Report Design]  or  [Browse Examples]          │
└─────────────────────────────────────────────────────────┘
```

**Primary actions:**
- "Add Report Design" (primary button)
- "Import from File" (secondary)

**Table columns:**
| Column | Header text |
|--------|-------------|
| Name | "Name" |
| Format | "Format" (PDF/Excel) |
| Status | "Status" (hide entirely unless team mode enabled) |
| Data points | "Data points" (replaces "Fields") |
| Created | "Created" |
| Last used | "Last used" |

**Row menu items:**
- "Edit Design"
- "Change Settings" (replaces "Edit Details")
- "Export"
- "Make a Copy" (replaces "Duplicate")
- "Remove"

**Edit Details dialog fields:**
| Field | Label |
|-------|-------|
| name | "Name" |
| description | "Description (optional)" |
| status | REMOVE (or show only in team mode as "Availability") |
| tags | REMOVE (power-user feature, add as optional later) |

---

#### PAGE: Reports (`/reports`)

**Title:** "Create a Report"
**Subtitle:** "Generate a report from your data"

**Missing connection alert:**
```
[Info icon] Before creating reports, you need to add a data source.
           [Add Data Source →]
```

**Missing template alert:**
```
[Info icon] You need at least one report design to create reports.
           [Add Report Design →]
```

**Form layout (simplified):**
```
┌─────────────────────────────────────────────────────────┐
│  Create a Report                                        │
│  Generate a report from your data                       │
│                                                         │
│  Which design?                                          │
│  [▼ Monthly Sales Report________________]               │
│                                                         │
│  What time period?                                      │
│  [This Month ▼] (or pick dates: [____] to [____])      │
│                                                         │
│  ┌─ Optional: Narrow down your data ─────────────┐     │
│  │  [Filter options only if applicable]           │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  [Create Report]                                        │
└─────────────────────────────────────────────────────────┘
```

**Date range quick picks:**
- "Today"
- "This Week"
- "This Month"
- "Last Month"
- "Custom dates..."

**Generate button:** "Create Report"

**Loading state:**
```
┌─────────────────────────────────────────────────────────┐
│  Creating your report...                                │
│                                                         │
│  [████████████░░░░░░░░░] 60%                           │
│                                                         │
│  Getting data from your database...                     │
│  This usually takes 1-2 minutes.                        │
│                                                         │
│  [Stop]                                                 │
└─────────────────────────────────────────────────────────┘
```

**Success state:**
```
┌─────────────────────────────────────────────────────────┐
│  ✓ Report created!                                      │
│                                                         │
│  Your report is ready. It will open in a new tab.       │
│                                                         │
│  [Download PDF]  [Create Another]                       │
│                                                         │
│  Want this report automatically?                        │
│  [Set Up Automatic Reports →]                           │
└─────────────────────────────────────────────────────────┘
```

---

#### PAGE: Jobs (`/jobs`)

**Title:** "Report Progress"
**Subtitle:** "See your reports being created"

**Empty state:**
```
┌─────────────────────────────────────────────────────────┐
│           [Clock Icon]                                  │
│                                                         │
│     No reports in progress                              │
│                                                         │
│     When you create reports, you'll see their           │
│     progress here.                                      │
│                                                         │
│     [Create a Report →]                                 │
└─────────────────────────────────────────────────────────┘
```

**Table columns:**
| Column | Header text |
|--------|-------------|
| ID | "Reference" |
| Template | "Report design" |
| Status | "Status" |
| Progress | "Progress" |
| Started | "Started" |
| Finished | "Finished" |

**Status chips:**
| Status | Display text | Color |
|--------|--------------|-------|
| pending | "Waiting" | Yellow |
| running | "Working..." | Blue |
| completed | "Done" | Green |
| failed | "Problem" | Red |
| cancelled | "Stopped" | Gray |

**Row menu items:**
- "View Details"
- "Download" (only when done)
- "Try Again" (only when failed, replaces "Retry")
- "Stop" (only when running/waiting, replaces "Cancel")

**Cancel job confirmation:**
```
┌─────────────────────────────────────────────────────────┐
│  Stop this report?                                      │
│                                                         │
│  [Warning Icon]                                         │
│                                                         │
│  The report won't be created. You can start             │
│  it again anytime.                                      │
│                                                         │
│  [Keep Creating]  [Stop Report]                         │
└─────────────────────────────────────────────────────────┘
```

---

### 7.2 Global Components

#### Toast Notifications

**Success toasts:**
| Action | Message |
|--------|---------|
| Connection added | "Data source added!" |
| Connection updated | "Changes saved" |
| Connection deleted | "Data source removed" |
| Template added | "Report design added!" |
| Template deleted | "Report design removed" |
| Report started | "Creating your report..." |
| Report completed | "Report ready! [View]" |
| Job cancelled | "Report stopped" |

**Error toasts (with recovery):**
| Error | Message | Action |
|-------|---------|--------|
| Connection failed | "Couldn't connect. Check settings." | [Edit Connection] |
| Save failed | "Couldn't save. Try again." | [Retry] |
| Network error | "Connection lost. Reconnecting..." | (auto-retry) |
| Unknown error | "Something went wrong." | [Report Problem] |

#### Confirmation Dialogs (Standard Pattern)

```
┌─────────────────────────────────────────────────────────┐
│  [Title - What's happening?]                            │
│                                                         │
│  [Icon matching severity]                               │
│                                                         │
│  [Clear explanation of consequences]                    │
│  [Any items that will be affected]                      │
│                                                         │
│  [Cancel/Safe option]  [Confirm/Action button]          │
└─────────────────────────────────────────────────────────┘
```

- Cancel button: Always left, always says "Cancel" or safe alternative
- Confirm button: Always right, verb describing action, colored by severity
  - Destructive (red): "Remove", "Stop", "Delete"
  - Warning (yellow): "Continue Anyway"
  - Normal (blue/green): "Save", "Create", "Confirm"

#### Empty States (Standard Pattern)

```
┌─────────────────────────────────────────────────────────┐
│           [Relevant Icon - muted color]                 │
│                                                         │
│     [What's missing - in plain language]                │
│                                                         │
│     [Why they might want to add it]                     │
│     [What benefit they'll get]                          │
│                                                         │
│     [Primary CTA]  [Secondary option if applicable]     │
└─────────────────────────────────────────────────────────┘
```

#### Loading States

**Full page loading:**
```
[Spinner] Loading...
```

**In-context loading:**
- Tables: Skeleton rows (keep existing)
- Buttons: Spinner replaces icon + "[Action]ing..." text
- Forms: Disabled state + spinner on submit button

#### Error States (Inline)

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ [What went wrong in plain language]                 │
│                                                         │
│  [Specific helpful suggestion]                          │
│                                                         │
│  [Try Again] [Get Help]                                 │
└─────────────────────────────────────────────────────────┘
```

---

### 7.3 Setup Wizard Rewrite

#### Step 1: "Where's your data?"

**Title:** "Where's your data?"
**Subtitle:** "Connect to your database or spreadsheet"

**Quick options:**
```
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  [Demo Icon]      │  │  [Cloud Icon]     │  │  [Server Icon]    │
│                   │  │                   │  │                   │
│  Try Demo Data    │  │  Cloud Database   │  │  My Own Server    │
│  Explore with     │  │  Supabase, etc.   │  │  PostgreSQL,      │
│  sample data      │  │                   │  │  MySQL, etc.      │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

**For "My Own Server":**
- Simplified form with only essential fields visible
- "Have a connection URL? Paste it here" option
- Auto-detect database type from URL

#### Step 2: "What should your report look like?"

**Title:** "What should your report look like?"
**Subtitle:** "Add a design that we'll fill with your data"

**Options:**
```
┌───────────────────┐  ┌───────────────────┐
│  [Preview]        │  │  [Upload Icon]    │
│                   │  │                   │
│  Use a Template   │  │  Upload My Own    │
│  Start with a     │  │  PDF or Excel     │
│  ready-made       │  │  file             │
│  design           │  │                   │
└───────────────────┘  └───────────────────┘
```

**For "Upload My Own":**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              Drag your file here                        │
│                                                         │
│              or [Choose File]                           │
│                                                         │
│              PDF or Excel files (.pdf, .xlsx, .xls)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Step 3: "Let's connect your data"

**Title:** "Let's connect your data"
**Subtitle:** "We found these fields in your design"

**Auto-mapped preview:**
```
┌─────────────────────────────────────────────────────────┐
│  We matched these automatically:                        │
│                                                         │
│  {{customer_name}} → customers.name          ✓ Matched  │
│  {{order_total}} → orders.total_amount       ✓ Matched  │
│  {{order_date}} → orders.created_at          ✓ Matched  │
│  {{product_list}} → (needs setup)            ⚠ Review   │
│                                                         │
│  [Looks Good]  or  [Let Me Adjust]                      │
└─────────────────────────────────────────────────────────┘
```

---

### 7.4 Accessibility Specifications

#### Keyboard Navigation
- All interactive elements focusable via Tab
- Escape closes any modal/drawer/menu
- Enter activates focused button
- Arrow keys navigate within menus and tables
- Cmd+K opens command palette

#### Screen Reader
- All icons have `aria-label`
- Status changes announced via `aria-live="polite"`
- Form errors announced via `aria-describedby`
- Loading states announced via `aria-busy`

#### Focus Management
- Modal opens → focus moves to first interactive element
- Modal closes → focus returns to trigger element
- Drawer opens → focus moves inside drawer
- Form submit → focus moves to first error or success message

---

## Implementation Priority

### P0 (Must have for usability)
1. Copy changes (Steps 3, 7.1-7.3)
2. Simplified report creation flow (Step 5)
3. Inline error messages with recovery (Step 4)
4. Demo data mode for first-time users
5. Progress checklist on dashboard

### P1 (High impact improvements)
1. Setup wizard simplification (Step 5, 7.3)
2. Date range quick picks
3. Connection form improvements (auto-test, better errors)
4. "Undo" for destructive actions
5. Contextual help tooltips

### P2 (Polish and delight)
1. Success celebrations
2. Email notifications
3. Time estimates on jobs
4. High contrast mode
5. Report problem link in errors

---

*End of UX Audit*
