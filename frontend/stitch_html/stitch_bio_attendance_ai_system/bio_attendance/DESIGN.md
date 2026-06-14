---
name: Bio Attendance
colors:
  surface: '#fff8f2'
  surface-dim: '#e4d9c8'
  surface-bright: '#fff8f2'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fef2e1'
  surface-container: '#f8ecdb'
  surface-container-high: '#f2e7d6'
  surface-container-highest: '#ece1d0'
  on-surface: '#201b11'
  on-surface-variant: '#4f4632'
  inverse-surface: '#363024'
  inverse-on-surface: '#fbefde'
  outline: '#827660'
  outline-variant: '#d4c5ab'
  surface-tint: '#785900'
  primary: '#785900'
  on-primary: '#ffffff'
  primary-container: '#ffc107'
  on-primary-container: '#6d5100'
  inverse-primary: '#fabd00'
  secondary: '#705d00'
  on-secondary: '#ffffff'
  secondary-container: '#fcd400'
  on-secondary-container: '#6e5c00'
  tertiary: '#006877'
  on-tertiary: '#ffffff'
  tertiary-container: '#00defd'
  on-tertiary-container: '#005e6c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdf9e'
  primary-fixed-dim: '#fabd00'
  on-primary-fixed: '#261a00'
  on-primary-fixed-variant: '#5b4300'
  secondary-fixed: '#ffe16d'
  secondary-fixed-dim: '#e9c400'
  on-secondary-fixed: '#221b00'
  on-secondary-fixed-variant: '#544600'
  tertiary-fixed: '#a5eeff'
  tertiary-fixed-dim: '#00daf8'
  on-tertiary-fixed: '#001f25'
  on-tertiary-fixed-variant: '#004e5a'
  background: '#fff8f2'
  on-background: '#201b11'
  surface-variant: '#ece1d0'
typography:
  display:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 24px
  margin-mobile: 16px
  sidebar-width: 260px
---

## Brand & Style
The brand personality is professional, authoritative, and technologically advanced, tailored for corporate and industrial environments. It balances the high-tech nature of AI biometrics with the reliability expected of enterprise human resources software.

The design style follows a **Corporate Modern** aesthetic with a lean toward **Minimalism**. It prioritizes clarity and efficiency through a high-contrast interface, ample whitespace, and a rigid adherence to a structured grid. The visual narrative communicates precision and security, ensuring that complex data remains legible and administrative tasks feel effortless.

## Colors
The palette is rooted in a "Clean Office" spectrum. The primary workspace is built on **Pure White (#FFFFFF)** for maximum clarity, with **Off-white (#F8F9FA)** used for structural grouping and background depth.

**Golden Yellow (#FFC107)** serves as the primary action color, providing high visibility for key interactions without compromising the professional tone. Text hierarchy is managed through scales of **Dark Gray**, ensuring deep contrast for body copy and a softer profile for metadata. The **Soft Yellow (#FEF3C7)** is reserved exclusively for subtle state indications, such as active navigation or highlighted data rows.

## Typography
**Inter** is utilized across all levels to maintain a systematic and utilitarian feel. The type system relies on tight tracking for headlines to create a "dense" professional look, while body copy utilizes generous line heights for long-form data reading.

- **Headlines:** Use Bold and Semi-Bold weights to establish clear information architecture.
- **Labels:** Small caps or slightly tracked uppercase is used for category headers and table headers to distinguish them from interactive data.
- **Logo:** The brand name should be rendered in Inter Bold, using optical kerning for a solid, architectural presence.

## Layout & Spacing
The layout employs a **Fixed Grid** philosophy on desktop to ensure data consistency, transitioning to a fluid model for mobile devices. 

- **Desktop:** 12-column grid with 24px gutters. A permanent 260px sidebar occupies the left edge.
- **Mobile:** Single column with 16px side margins. 
- **Spacing Rhythm:** Based on a 4px baseline. Use 16px (md) for standard component padding and 24px (lg) for section separation. Large dashboards should utilize 32px (xl) margins to prevent cognitive overload.

## Elevation & Depth
Depth is achieved through **Tonal Layers** supplemented by very soft, ambient shadows. 

- **Level 0 (Background):** #F8F9FA.
- **Level 1 (Cards/Surface):** #FFFFFF with a 1px border (#E5E7EB) and a subtle shadow (0px 4px 12px rgba(0, 0, 0, 0.05)).
- **Level 2 (Overlays/Dropdowns):** #FFFFFF with a more pronounced shadow (0px 8px 24px rgba(0, 0, 0, 0.1)).

Avoid heavy blurs or colorful glows. The intent is to make elements feel like physical cards sitting on a desk under neutral office lighting.

## Shapes
The design system uses a mixed-radius strategy to differentiate between structural containers and interactive elements. 

- **Containers/Cards:** 12px (rounded-lg) to soften the large surface areas of data tables and charts.
- **Interactive Elements:** Buttons and Input fields use a tighter 8px (rounded) radius to look more precise and "clickable."
- **Status Indicators:** Pills and tags should use a fully rounded (pill-shaped) radius to contrast against the rectangular grid.

## Components
### Buttons
- **Primary:** Solid #FFC107 background with #1F2937 text. 8px radius.
- **Secondary:** Outline (#E5E7EB) with #1F2937 text. On hover, background shifts to #F8F9FA.

### Navigation (Sidebar)
- Text-only menu items using `body-md` Semi-Bold.
- **Active State:** A 4px vertical border on the left (#FFC107) and a full-width background tint of #FEF3C7. Text remains #1F2937 for readability.

### Input Fields
- White background with #E5E7EB border.
- **Focus State:** 2px solid #FFC107 border with a subtle yellow outer glow. 
- Labels sit above the field in `label-md` gray.

### Cards
- White surface, 12px radius, 1px border (#E5E7EB).
- Includes a subtle shadow for elevation. Used for dashboard widgets, employee profiles, and attendance logs.

### Chips/Tags
- Used for attendance status (e.g., "Present", "Absent", "Late"). 
- Use small, low-saturation background tints with darker text for status-specific colors (Green for Present, Red for Absent).