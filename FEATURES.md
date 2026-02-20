# NeuraReport - Complete Feature Inventory

A comprehensive document outlining all features (major and minor) in the NeuraReport application.

---

## Table of Contents

1. [Core/Major Features](#coremajor-features)
2. [AI-Powered Features](#ai-powered-features)
3. [Document Intelligence (DocAI)](#document-intelligence-docai)
4. [Knowledge Management](#knowledge-management)
5. [Search & Discovery](#search--discovery)
6. [Visualization & Diagrams](#visualization--diagrams)
7. [Data & Database Features](#data--database-features)
8. [Export & Distribution](#export--distribution)
9. [Workflow Automation](#workflow-automation)
10. [Frontend Features](#frontend-features)
11. [Infrastructure & Security](#infrastructure--security)
12. [Integrations](#integrations)
13. [Testing & Development](#testing--development)

---

## Core/Major Features

### 1. Report Generation & Management
- PDF report generation with dynamic template mapping
- Excel report generation with data mapping
- Async job processing for large report batches
- Report run history and execution tracking
- Batch discovery for multi-template report generation
- Report scheduling with cron-like triggers
- Report distribution and scheduling management
- Template-to-report pipeline with data binding

### 2. Database Connectivity
- Multi-database support: PostgreSQL, MySQL, MSSQL, MariaDB, SQLite, MongoDB, Elasticsearch
- Connection management (CRUD operations)
- Connection health checking and validation
- Schema browser for database exploration
- Data preview from database tables
- Connection pooling and lifecycle management
- Credential encryption (Fernet symmetric encryption)

### 3. Template Management
- PDF and Excel template support
- Template verification and validation
- Template upload and import/export (ZIP archives)
- Template catalog browsing
- AI-powered template editing and suggestions
- Template duplication and versioning
- Manual HTML template editing
- AI chat-based template editing with real-time changes
- Mapping preview and approval workflow
- Corrections preview for data mapping
- Undo/redo for template edits
- Template recommendations based on document analysis
- Saved charts management per template
- Chart suggestions for templates

### 4. Document Management
- Document CRUD operations
- Version history tracking
- Comments and annotations
- Real-time collaboration sessions
- Presence awareness for collaborators
- PDF operations:
  - Merge multiple PDFs
  - Watermark addition
  - Content redaction
  - Page reordering

### 5. Ingestion & Import
- File upload (single, bulk, ZIP archives)
- URL-based ingestion and download
- Structured data import (JSON, XML, YAML)
- Web clipper (URL clipping with HTML cleaning)
- Web clipper selection mode
- Folder watcher with auto-import
- Audio/video transcription
- Email ingestion and parsing
- Email inbox generation
- Voice memo transcription

---

## AI-Powered Features

### 6. AI Writing Services
- Grammar checking with language support and strict mode
- Text summarization with multiple output styles
- Text rewriting with tone selection
- Content expansion with examples and details
- Translation to multiple languages with formatting preservation
- General content generation with contextual prompts

### 7. AI Spreadsheet Features
- Natural language to formula conversion
- Data quality analysis and cleaning
- Anomaly detection in datasets
- Predictive analysis on data
- Formula explanation in natural language
- Formula suggestions based on data analysis

### 8. AI Agents (5 Specialized Agents)

#### Research Agent
- Deep-dive research and report compilation

#### Data Analyst Agent
- Answers questions about data with chart generation

#### Email Draft Agent
- Compose emails based on context

#### Content Repurposing Agent
- Transform content to multiple formats:
  - Tweets
  - LinkedIn posts
  - Blog articles
  - Slides
  - Video scripts
  - Infographics
  - Podcast notes
  - Press releases
  - Executive summaries

#### Proofreading Agent
- Comprehensive style and grammar checking

### 9. Natural Language to SQL (NL2SQL)
- SQL query generation from natural language
- Query execution with result pagination
- Query explanation in plain English
- Saved queries management
- Query history tracking
- History entry deletion

---

## Document Intelligence (DocAI)

### 10. Document Parsing & Extraction
- Invoice parsing and extraction
- Contract analysis and risk assessment
- Resume/CV parsing and job matching
- Receipt scanning and data extraction
- Document classification by type
- Named entity extraction (persons, organizations, locations, dates, values)

### 11. Advanced Document Analysis
- Semantic document search using embeddings
- Document comparison and diff analysis
- Compliance checking against regulations (GDPR, HIPAA, SOC2)
- Multi-document summarization with source references

### 12. Document Q&A System
- Session-based Q&A conversations
- Add/remove documents to sessions
- Ask questions on document collections
- Response feedback mechanism
- Response regeneration capability
- Chat history tracking

---

## Knowledge Management

### 13. Document Library
- Document library management
- Collections organization
- Auto-tagging based on content
- Related documents suggestions
- Knowledge graph generation
- FAQ generation from documents

### 14. Search & Organization
- Full-text search with indexing
- Semantic search using embeddings
- Tag management and hierarchies
- Favorites/bookmarking system

---

## Search & Discovery

### 15. Search Capabilities
- Full-text search with pagination
- Semantic search using embeddings
- Regular expression search (with ReDoS protection)
- Boolean search (AND, OR, NOT operators)
- Search and replace across documents
- Similar document detection
- Saved searches management
- Search indexing and analytics

---

## Visualization & Diagrams

### 16. Diagram Generation
- Flowchart generation from descriptions
- Mind map generation from content
- Organization chart creation
- Timeline visualization
- Gantt chart generation
- Network graph visualization
- Kanban board generation
- Sequence diagram creation
- Word cloud generation
- Table-to-chart conversion
- Sparklines in text
- Mermaid export support

---

## Data & Database Features

### 17. Data Enrichment
- Built-in enrichment sources:
  - Company info
  - Address standardization
  - Currency exchange
- Custom enrichment source creation
- Data enrichment with multiple sources
- Enrichment preview on samples
- Cache statistics and management
- Cache clearing functionality

### 18. Cross-Database Federation
- Virtual schema creation spanning multiple databases
- AI-suggested joins between tables across connections
- Federated query execution across databases

### 19. Spreadsheet Features
- Spreadsheet creation and CRUD
- Cell updates and editing
- Sheet management (add sheets)
- Conditional formatting
- Data validation rules
- Freeze panes
- Pivot table generation
- Excel export

### 20. Connectors
- Connector type listing
- Connector type filtering by category
- Database connector support
- Cloud storage connector support
- Test connection verification
- OAuth-based authentication for SaaS connectors

---

## Export & Distribution

### 21. Multi-Format Export
- PDF export
- PDF/A (archival) export
- DOCX (Word) export
- PPTX (PowerPoint) export
- ePub export
- LaTeX export
- Markdown export
- HTML export
- Bulk export with ZIP packaging

### 22. Distribution Channels
- Email campaign distribution
- Portal publishing with access controls
- Embed code generation for websites
- Slack channel integration
- Microsoft Teams webhook integration
- Webhook delivery system
- Export job tracking and status

---

## Workflow Automation

### 23. Workflow Management
- Workflow creation and management
- Workflow execution with async support
- Workflow triggers (event-based, scheduled)
- Approval workflows with pending approvals
- Workflow execution history
- Execution status tracking

### 24. Report Scheduling
- Schedule creation with cron expressions
- Enable/disable schedules
- Trigger/pause/resume schedules
- Schedule list viewing
- Schedule-based report generation

---

## Frontend Features

### 25. Pages & Containers (36 Feature Areas)
- Activity Page (activity tracking)
- Agents Page (AI agent management)
- Analyze Page (document analysis)
- Connections Page (database connections)
- Connectors Page (connector management)
- Dashboard Page (main dashboard)
- Dashboard Builder (custom dashboard design)
- Design Page (branding and design)
- Document Editor (collaborative document editing)
- Document Q&A (Q&A interface)
- Enrichment Configuration (data enrichment setup)
- Federation/Schema Builder (federated query building)
- Generate Page (report generation)
- History Page (activity/change history)
- Ingestion Page (document import)
- Jobs Page (job monitoring)
- Knowledge Page (knowledge library)
- OpsConsole (operations monitoring)
- Query Builder (SQL/NL2SQL builder)
- Reports Page (report management)
- Schedules Page (schedule management)
- Search Page (search interface)
- Settings Page (user preferences)
- Setup Wizard (initial configuration)
- Spreadsheet Editor (collaborative spreadsheet editing)
- Statistics Page (usage analytics)
- Summary Page (summary generation)
- Synthesis Page (document synthesis)
- Templates Page (template management)
- Visualization Page (diagram generation)
- Workflow Builder (workflow design)

### 26. UI Components
- Data Table with sorting/filtering
- Drawer components
- Modal dialogs
- Form components (inputs, selectors, etc.)
- Layout components
- Feedback components (toasts, alerts)
- AI-powered component suite
- UX governance components

### 27. Design & Branding
- Brand kit creation and management
- Color palette generation with harmony types
- Theme creation and management
- Brand kit application to documents
- Theme activation and switching
- Design system management

### 28. Dashboards
- Dashboard creation
- Dashboard updates
- Dashboard listing
- Dashboard-based analytics visualization

---

## Analytics & Monitoring

### 29. Usage Analytics
- Dashboard analytics with usage metrics
- Token consumption tracking
- Report generation statistics
- Search analytics
- Job statistics by status (succeeded, failed, running, queued)
- Time-period analytics (today, week, month)
- Bulk operations tracking
- Usage insights and trends

### 30. System Health & Monitoring
- Detailed health check endpoint
- Token usage reporting
- Email/SMTP status verification
- Scheduler status monitoring
- OpenAI connection status
- Directory access verification
- Memory usage tracking
- Dependency status checks
- OpsConsole page with all diagnostics

### 31. Jobs Management
- Jobs listing with filtering
- Active jobs view
- Job details retrieval
- Job cancellation
- Job retry functionality
- Background job execution
- Async job tracking and status

---

## Infrastructure & Security

### 32. Authentication & Authorization
- JWT-based authentication
- FastAPI-Users integration
- API key authentication
- User registration and login
- User profile management
- Password hashing (bcrypt)

### 33. Security Measures
- Credential encryption (Fernet)
- Path traversal prevention
- ReDoS attack prevention (regex validation)
- Memory exhaustion protection
- SQL injection prevention (parameterized queries)
- Rate limiting
- CORS protection
- Input validation
- Request sanitization

### 34. Configuration Management
- Environment-based configuration
- Settings management
- Secret management
- Credentials encryption

### 35. Background Processing
- APScheduler for task scheduling
- Prefect for workflow orchestration
- Async job queue
- Background task execution
- Event-based task processing
- NDJSON event streaming

### 36. State Management
- SQLite-based state store
- JSON state persistence
- State access layer
- Connection state management
- Job state tracking
- Template state management

### 37. Error Handling & Middleware
- Custom exception handlers
- Error logging
- Correlation ID tracking
- Error response formatting
- Rate limiting middleware
- Request logging middleware
- Response middleware

---

## Integrations

### 38. LLM Providers
- Claude Code CLI (primary — no API key needed, uses authenticated CLI session)
- liteLLM abstraction layer (unified fallback across providers)
- OpenAI support (optional fallback)
- Anthropic API support (optional direct access)
- Google Gemini support (optional)
- DeepSeek provider support
- Ollama local LLM support
- Azure OpenAI support
- LLM circuit breaker pattern (automatic failover)
- LLM response disk caching

### 39. Cloud Storage Services
- Google Cloud Storage
- AWS S3
- Microsoft Azure Blob Storage
- Dropbox
- SFTP
- OneDrive

### 40. Productivity Integrations
- Slack
- Microsoft Teams
- Notion API *(planned — not yet implemented)*
- Google Docs OAuth *(planned — not yet implemented)*
- Outlook/Gmail integration *(planned — not yet implemented)*

### 41. Database Support
- SQLite (local)
- PostgreSQL
- MySQL/MariaDB
- MSSQL
- MongoDB
- Elasticsearch
- Snowflake
- BigQuery
- DuckDB

---

## Testing & Development

### 42. Testing Infrastructure
- Vitest unit tests
- Playwright E2E tests
- UI tests (@ui flag)
- Accessibility tests (@a11y flag)
- Visual regression tests (@visual flag)
- Visual snapshot updates
- Comprehensive API client tests

### 43. Build & Deployment
- Vite build system
- npm package management
- ESLint code quality
- pre-commit hooks
- Docker support
- Uvicorn ASGI server

### 44. Logging & Monitoring
- Structured logging
- Error log file output
- Request correlation tracking
- Health check monitoring
- Token usage tracking

---

## Backend Service Architecture

### 45. Service Layers (93+ Service Directories)
- Agent services (5 agent types)
- AI services (writing, spreadsheet, LLM integration)
- Analytics services
- Analysis services
- Chart services
- Connection services
- Connector services (database, storage)
- Contract builder services
- Dashboard services
- Dataframe services
- Design services
- DocAI services with specialized parsers
- Document services
- Documents ingestion/parsing
- Email services
- Enrichment services (3+ sources)
- Excel services
- Export services
- Extraction services
- Federation services
- Generate services
- Generator services
- Ingestion services (multiple sources)
- Job services
- Knowledge services
- LLM services (liteLLM integration)
- Mapping services
- NL2SQL services
- Prompt services
- Recommendations services
- Render services
- Report services
- Search services
- Spreadsheet services
- State management services
- Summary services
- Synthesis services
- Template services
- Utilities services
- Visualization services
- Workflow services

---

## Additional Features (Discovered via Forensic Audit — January 2026)

### Document Security
- PDF digital signing capability

### Jobs & Background Processing
- Recovery daemon for automatic retry of failed/stale jobs
- Error classifier (transient vs. permanent failure detection)
- HMAC-SHA256 webhook signing for job notifications
- Webhook retry with exponential backoff

### Enhanced Analysis
- Enhanced analysis orchestrator (multi-stage document analysis)
- Enhanced extraction service (advanced content extraction)
- Connector resilience (circuit breaker pattern for external connectors)

### API Infrastructure
- Idempotency endpoint support (request deduplication)
- UX governance API (frontend safety contracts)
- State namespace API (key-value state storage)
- Governance guards service (irreversible action protection)

### Frontend UX Governance
- Intent audit tracking system
- Idempotency key generation (client-side)
- Command palette (keyboard-driven navigation)
- Keyboard shortcuts system
- Network status banner (connectivity awareness)
- Offline mode banner
- Draft recovery system (auto-save and restore)
- Edit history timeline
- Success celebration animation
- Heartbeat status badge
- Favorite/bookmark button
- Global search in navigation
- Notification center
- Breadcrumbs navigation
- AI usage notice component
- Irreversible boundaries (confirmation gates)
- Navigation safety guards (unsaved changes protection)
- Regression guards (prevent accidental downgrades)
- Time expectations UI (estimated durations)
- Workflow contracts enforcement
- Background operations tracking

---

## Technical Libraries & Frameworks

### 46. Frontend Stack
- React 19
- Vite 7
- MUI v7 (Material UI)
- Zustand 5 (state management)
- TipTap (rich text editing)
- Handsontable/HyperFormula (spreadsheets)
- ECharts/Recharts (charts)
- React Flow (diagrams)
- Y.js (real-time collaboration)
- Playwright (E2E testing)

### 47. Backend Stack
- FastAPI
- SQLAlchemy
- Pydantic
- APScheduler
- Prefect
- liteLLM

### 48. Data Processing
- Pandas
- DuckDB
- NumPy
- spaCy (NLP)
- scikit-learn
- statsmodels

### 49. Document Processing
- PyMuPDF
- pdfplumber
- reportlab
- python-docx

---

## Cross-Page Data Sharing (Phase 9)

### 50. Cross-Feature Data Flow
- SendToMenu component for contextual data export to other features
- ImportFromMenu component for pulling data from other features
- Declarative input/output contracts per feature (OutputType, TransferAction, FeatureKey)
- useCrossPageActions hook for seamless inter-page transfers
- useIncomingTransfer hook for detecting and handling incoming data
- useSharedData hook for accessing data passed between features
- crossPageStore (Zustand) for transfer state management
- ConnectionSelector and TemplateSelector reusable picker components
- Type-safe data passing supporting: TEXT, RICH_TEXT, TABLE, DOCUMENT, DIAGRAM, DATASET, REPORT, ANALYSIS

### 51. AI QA Agent (`@neurareport/ai-qa-agent`)
- Standalone npm package for AI-powered E2E testing
- Framework-agnostic: works with React, Vue, Angular, plain HTML
- Built-in UI framework presets (MUI, Tailwind, Bootstrap, Ant Design, Chakra, shadcn/ui)
- Vision support with Claude screenshot analysis
- Smart stuck detection and re-planning
- Cross-session learning from previous test runs
- Action caching for faster replay
- Persona modifiers (default, impatient, confused, power-user, accessibility, mobile, slow-network)
- QA profiles (general-purpose, neurareport)
- Detailed evidence output (screenshots, network logs, LLM conversations, perception logs)
- Structured failure categorization for debugging

---

## Feature Summary

| Category | Count |
|----------|-------|
| Core/Major Features | 26 |
| AI-Powered Features | 16 |
| Document Intelligence | 12 |
| Knowledge Management | 8 |
| Search Features | 8 |
| Visualization Types | 12 |
| Data Features | 20 |
| Export Formats | 8 |
| Distribution Channels | 6 |
| Workflow Features | 6 |
| Frontend Pages | 33 |
| UI Components | 8 |
| Cross-Page Data Sharing | 10 |
| AI QA Agent | 12 |
| Security Features | 12 |
| Integrations | 22 |
| Backend Services | 93+ |
| Additional Discovered Features | 33 |

**Total Features Identified: 210+**

---

## Key Technical Capabilities

1. **Multi-source document ingestion** - files, URLs, web clips, emails, transcriptions
2. **Real-time collaborative editing** - with presence awareness
3. **AI-powered document processing** - parsing, classification, analysis
4. **Cross-database federation** - querying across multiple data sources
5. **Natural language interfaces** - for SQL, formulas, and content generation
6. **Rich visualization** - 15+ diagram types
7. **Comprehensive export** - 8+ formats
8. **Workflow automation** - with triggers and approvals
9. **Advanced search** - full-text, semantic, regex, boolean
10. **Token-based usage tracking** - and analytics
11. **Async batch processing** - for large-scale operations
12. **Modular AI agent architecture** - for specialized tasks

---

*This document represents a comprehensive, enterprise-grade document processing and reporting platform with deep AI integration, multi-source connectivity, and extensive automation capabilities.*

*Updated: February 2026*
