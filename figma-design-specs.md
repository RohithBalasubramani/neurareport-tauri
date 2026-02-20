# Neuract Demo - Figma Design Specifications

**File Key:** 1Hp9IvJjDcsI4MXJdbOqyo
**Extracted Date:** 2026-01-25

---

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Screen Specifications](#screen-specifications)
5. [Component Library](#component-library)
6. [Asset URLs](#asset-urls)

---

## Design System Overview

### Application Type
IoT/Device Management Dashboard - "Neuract Demo"

### Screen Resolution
- **Primary:** 1536 x 960px
- **Content Area:** 1536 x 912px (excluding taskbar)

### Layout Structure
- **Left Sidebar:** 250px width - Navigation menu
- **Main Content:** Flexible width
- **Right Panel (optional):** 400px - Device details panel
- **Bottom Taskbar:** 48-50px height

---

## Color Palette

### Grey Scale (Primary)
| Token | Hex Value | Usage |
|-------|-----------|-------|
| grey/white | #FFFFFF | Background |
| grey/200 | #F9F9F8 | Secondary background, sidebar |
| grey/300 | #F1F0EF | Input backgrounds, cards |
| grey/400 | #E9E8E6 | Hover states, active items |
| grey/500 | #E2E1DE | Borders, dividers |
| grey/600 | #DAD9D6 | Borders |
| grey/700 | #CFCECA | Borders, strokes |
| grey/800 | #BCBBB5 | Dividers, taskbar borders |
| grey/900 (main) | #8D8D86 | Secondary text, icons |
| grey/1000 | #82827C | Tertiary text |
| grey/1100 | #63635E | Primary text, labels |
| grey/1200 | #21201C | Headings, titles |

### Neutral Colors
| Token | Hex Value | Usage |
|-------|-----------|-------|
| Neutral/200 | #E5E7EB | Tab borders |
| Neutral/400 | #9CA3AF | Placeholder text |
| Neutral/500 | #6B7280 | Secondary labels |

### Accent Colors
| Token | Hex Value | Usage |
|-------|-----------|-------|
| Primary Green | #007E60 | Active tab border |
| Green Background | #EBFEF6 | Active tab background |
| Green Text | #02634E | Active tab text |
| Dark Text | #374151 | Inactive tab text |

### Status Colors
| Status | Color | Usage |
|--------|-------|-------|
| Reachable/Online | Green (#007E60 area) | Status indicator |
| Unreachable/Offline | Red indicator | Status indicator |
| Running | Grey | AI agent status |

### Gradient
- **AI Assistant Panel:** Linear gradient from #F9F9F8 to #88A6FF (258.88%)
- **Notification Panel:** Linear gradient from #F1F0EF to #A1D3FF (258.88%)

---

## Typography

### Font Families
1. **Tomorrow** - Headings and titles
2. **Inter** - Body text, labels, UI elements
3. **Lato** - Tabs, input fields, paragraphs

### Text Styles

| Style Name | Font | Weight | Size | Line Height | Letter Spacing |
|------------|------|--------|------|-------------|----------------|
| Page Title | Tomorrow | Medium (500) | 24px | normal | 0 |
| Section Title | Tomorrow | Medium (500) | 20px | normal | 0 |
| Navigation Item | Inter | Medium (500) | 16px | normal | 0 |
| Label/Medium | Lato | Medium (500) | 14px | 16px | 0 |
| Paragraph/Small | Lato | Regular (400) | 14px | 20px | 0 |
| 16/para-Reg | Lato | Regular (400) | 16px | 1.4 | 0.64px |
| Small Text | Inter | Medium (500) | 12px | normal | 0 |
| Tiny Text | Inter | Medium (500) | 10px | normal | 0 |

---

## Screen Specifications

### Screen 1: Map View with AI Chat (Node: 634:4257)
**Purpose:** Connected devices visualization on floor plan with AI assistant

**Layout:**
- Left sidebar: Settings navigation (250px)
- Main content: Floor plan map view
- Floating AI chat input at bottom center
- Device selection box (dashed border)

**Key Elements:**
- Search input with filter button
- Map/Table view toggle
- Zoom controls (+/- buttons)
- Floor plan with 4 rooms
- Device icons (MFM 1-8, Router)
- AI assistant input: "What do to want to know..."
- Microphone icon for voice input

**Dimensions:**
- Room squares: 380x380px
- Device icons: 54x35.586px (MFM meters)
- Router icon: 67.444x78.554px
- AI chat panel: 394x114px

---

### Screen 2: Home Screen with Notification (Node: 634:6288)
**Purpose:** Desktop/home view with device connection notification

**Layout:**
- Full-screen grey background (#F1F0EF)
- Floating notification card
- Bottom taskbar

**Key Elements:**
- Date/time display: "10:34  26 Nov 2025"
- Notification card with blue gradient
- Message: "New Device connected"
- Sub-message: "Say 'Add Setting' to add settings to the devices"
- Close button (X)

**Dimensions:**
- Notification card: 394x155px
- Close button: 20x20px

---

### Screen 3: Map View with Status Indicators (Node: 634:3531)
**Purpose:** Device map showing connection status

**Layout:**
- Same as Screen 1
- Different device status indicators (some red/alert)

**Key Differences:**
- MFM 5 shows red/alert status
- No AI chat visible
- Clean map view

---

### Screen 4: Map View with Device Details Panel (Node: 634:4628)
**Purpose:** Device selection with detailed info panel

**Layout:**
- Left sidebar: 250px
- Main content: Map view (reduced)
- Right panel: Device details (400px)

**Device Details Panel Content:**
- Device name: "MFM 3"
- Device image/icon with status dots
- Expandable sections:
  1. **Device Details**
     - IP Address: 192.168.1.1
     - Status: Reachable (green dot)
     - Protocol: Modbus
     - Port: 502
  2. **Connected Gateway Details**
     - Name: Gate way Router 2
     - Status: Reachable
     - IP Address: 192.168.1.1
     - Protocol: Modbus
     - Unit ID: 1
     - Mode: Network
  3. **Database connection**
     - File name: Temperature.xslv
- Action button: "Ping"

**Dimensions:**
- Details panel: 400x872px
- Section headers: 40px height
- Row items: 40px height

---

### Screen 5: Table View with Device List (Node: 634:5136)
**Purpose:** Tabular view of all connected devices

**Layout:**
- Left sidebar: 250px
- Main content: Data table
- Right panel: Device details (400px)

**Table Columns:**
| Column | Width | Content |
|--------|-------|---------|
| Devices | 240px | Device icon + name |
| Status | 145.5px | Status indicator + label |
| IP Address | 145.5px | IP address text |
| Connected DB | 145.5px | Database filename |
| Mode | 145.5px | Network/Wired |

**Table Row Data:**
- Device type: Multi function meter
- Status: Reachable/Unreachable
- IP: 192.168.1.20
- DBs: Temp.db, MFM.db
- Modes: Network, Wired

**Row Height:** 60px
**Header Height:** 60px

---

### Screen 6: Database Settings Tab (Node: 634:5882)
**Purpose:** Database configuration and data table view

**Layout:**
- Left sidebar with temperature list
- Main content: Editable data grid

**Left Panel Items:**
- Temperature 1 through Temperature 7

**Data Grid:**
- Editable columns with pencil icon
- "Add New" button (+ icon)
- Column headers: "column 1" (editable)
- Cell content: "column 1" placeholder

**Dimensions:**
- Left panel item height: ~27px
- Grid cell: Variable width
- Add New button: Located in header row

---

### Screen 7: Map View with AI Assistant Expanded (Node: 634:3887)
**Purpose:** Map view with expanded AI query panel

**Layout:**
- Same map layout as Screen 1
- AI panel in top-right corner (expanded)

**AI Panel Content:**
- Avatar icon (animated dots)
- Input field: "What do to want to know..."
- Microphone button
- Helper text: "Select & Drag on map to ask"
- Close button

**Dimensions:**
- AI panel: 394x114px
- Position: Top-right of main content

---

## Component Library

### Navigation Sidebar
```
Width: 250px
Background: grey/200 (#F9F9F8)
Padding: 16px horizontal, 20px vertical
Border-radius: 8px
```

**Navigation Items:**
- Home (home icon)
- Network (network_node icon)
- Plugged Devices (electrical_services icon) - **Active state**
- Devices (devices_other icon)
- Notification (notifications icon)
- Personalization (landscape_2_edit icon)
- AI Agent (smart_toy icon)
- Licensing and About (info icon)

**Item Styling:**
- Height: 40px
- Gap: 8px (icon to text)
- Active background: grey/400 (#E9E8E6)
- Icon size: 20x20px
- Text: Inter Medium 16px, grey/1100

### Tabs Component
```
Border-bottom: 1px solid #E5E7EB
Height: 40px
```

**Tab States:**
| State | Background | Border | Text Color |
|-------|------------|--------|------------|
| Active | #EBFEF6 | 2px #007E60 bottom | #02634E |
| Inactive | transparent | 1px #E5E7EB bottom | #374151 |

**Tab Padding:** 32px horizontal, 8px vertical

### Search Input
```
Width: 240px
Height: 40px
Background: grey/300 (#F1F0EF)
Border: 1px solid grey/500 (#E2E1DE)
Border-radius: 8px
Padding: 12px horizontal, 8px vertical
```

**Elements:**
- Search icon: 20x20px
- Placeholder: "Search" (Lato Regular 14px, #9CA3AF)

### Filter Button
```
Height: 40px
Background: grey/300 (#F1F0EF)
Border: 1px solid grey/500 (#E2E1DE)
Border-radius: 8px
Padding: 12px horizontal, 4px vertical
Gap: 8px
```

### View Toggle (Map/Table)
```
Background: white
Border: 1px solid grey/700 (#CFCECA)
Border-radius: 8px
```

**Options:**
- Map view (map icon)
- Table view (data_table icon) - Active: grey/500 background

### Zoom Controls
```
Background: rgba(77, 69, 61, 0.28)
Border: 1px solid #CFCFCF
Border-radius: 35px
Height: 40px
Padding: 12px horizontal, 8px vertical
Gap: 12px
```

**Icons:** minus (24x24px), plus (24x24px)

### Device Card (Map View)
**MFM Meter:**
- Icon size: 54x35.586px
- Label: Inter Medium 14px
- Background: Device illustration

**Router:**
- Icon size: 67.444x78.554px
- Label: "Router"

### Status Indicator
```
Dot size: 8x8px (circle)
Gap to text: 6px
```

| Status | Dot Color |
|--------|-----------|
| Reachable | Green |
| Unreachable | Red/Grey |

### Data Table
**Header:**
- Height: 60px
- Background: transparent
- Font: 14px (label style)
- Padding: 16px

**Content Cell:**
- Height: 60px
- Padding: 16px
- Vertical align: center

### AI Assistant Panel
```
Width: 394px
Height: 114px (collapsed) / variable (expanded)
Background: Linear gradient (grey/200 to blue)
Border-radius: 4px top corners
Box-shadow: 0px 4px 8.4px rgba(0,0,0,0.25)
Padding: 16px
```

**Input Field:**
- Height: 48px
- Background: grey/300
- Border: 1px solid grey/900
- Border-radius: 8px
- Padding: 16px

### Notification Card
```
Width: 394px
Background: Linear gradient (grey/300 to light blue)
Border-radius: 4px top corners
Padding: 16px
```

### Bottom Taskbar
```
Height: 48px
Background: grey/200 (#F9F9F8)
Border-top: 1px solid grey/800
```

**Sections:**
1. Left: App icons (view_compact_alt, activity, docs, AR, more)
2. Center: Layout previews (60x40px each)
3. Right: AI status, system tray (HDMI, WiFi, Volume, Settings), notifications, user avatar

### User Avatar
```
Size: 28x28px
Border: 1px solid grey/1000
Border-radius: 32px (circular)
```

### Scrollbar
```
Width: 20.156px
Background: #D9D9D9
Border-radius: 4px
```

---

## Asset URLs

### Icons (20x20px unless noted)
| Icon Name | Purpose |
|-----------|---------|
| view_compact_alt | Grid view |
| browse_activity | Activity |
| docs | Documents |
| view_in_ar | AR view |
| more_horiz | More options |
| home_17dp | Home navigation |
| network_node | Network navigation |
| electrical_services | Plugged Devices |
| devices_other | Devices navigation |
| notifications | Notifications |
| landscape_2_edit | Personalization |
| smart_toy | AI Agent |
| info | About/Info |
| search | Search |
| tune | Filter |
| map | Map view |
| data_table | Table view |
| remove | Zoom out |
| add_2 | Zoom in |
| location_on (35px) | Your Device marker |
| settings_input_hdmi | HDMI/Connection |
| wifi | WiFi status |
| volume_up | Volume |
| settings | Settings |
| mic | Microphone |
| close_small | Close button |
| router | Router device |

### Device Images
- MFM Meter (Multi-function meter): Various states
- Router: Network router illustration
- User Avatar: Profile image

---

## Interaction States

### Hover States
- Navigation items: Background change to grey/400
- Buttons: Slight opacity change
- Table rows: Background highlight

### Active/Selected States
- Navigation: grey/400 background
- Tabs: Green border, green background
- View toggle: grey/500 background
- Device on map: Selection box (dashed border)

### Focus States
- Inputs: Border color change to grey/900

---

## Responsive Considerations

### Fixed Elements
- Left sidebar: 250px (collapsible)
- Right panel: 400px (conditional)
- Bottom taskbar: 48px

### Flexible Elements
- Main content area: Fills remaining space
- Map/Table content: Scrollable
- Data grid: Horizontal scroll if needed

---

## Animation Notes

### AI Assistant Avatar
- Animated dots indicating "thinking" or "listening" state
- Pulse animation on voice input

### Notifications
- Fade in from bottom
- Auto-dismiss capability

### Panel Transitions
- Slide in from right (device details)
- Fade transitions for view changes

---

## File References

| Node ID | Screen Name | Description |
|---------|-------------|-------------|
| 634:4257 | Map + AI Chat | Main map view with AI assistant |
| 634:6288 | Home + Notification | Desktop with device notification |
| 634:3531 | Map + Status | Map view with status indicators |
| 634:4628 | Map + Details | Map with device details panel |
| 634:5136 | Table View | Tabular device list |
| 634:5882 | Database Settings | Database configuration tab |
| 634:3887 | Map + AI Expanded | Map with expanded AI panel |

---

*Generated from Figma file: Neuract-Demo*
*Figma URL: https://www.figma.com/design/1Hp9IvJjDcsI4MXJdbOqyo/Neuract-Demo*
