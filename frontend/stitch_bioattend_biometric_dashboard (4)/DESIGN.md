---
name: BioAttend Enterprise
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#7bd0ff'
  on-secondary: '#00354a'
  secondary-container: '#00a6e0'
  on-secondary-container: '#00374d'
  tertiary: '#bdc2ff'
  on-tertiary: '#131e8c'
  tertiary-container: '#7c87f3'
  on-tertiary-container: '#081486'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#c4e7ff'
  secondary-fixed-dim: '#7bd0ff'
  on-secondary-fixed: '#001e2c'
  on-secondary-fixed-variant: '#004c69'
  tertiary-fixed: '#e0e0ff'
  tertiary-fixed-dim: '#bdc2ff'
  on-tertiary-fixed: '#000767'
  on-tertiary-fixed-variant: '#2f3aa3'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter-desktop: 24px
  margin-desktop: 40px
  gutter-mobile: 16px
  margin-mobile: 16px
  container-max: 1440px
---

## Brand & Style

The design system is engineered for high-stakes enterprise environments where precision, reliability, and security are paramount. The brand personality is authoritative yet frictionless, balancing a sophisticated aesthetic with the utilitarian requirements of administrative and biometric software.

The visual style is **Corporate / Modern** with a focus on **Tonal Layering**. It avoids unnecessary ornamentation, instead using purposeful white space and subtle value shifts to establish hierarchy. The interface prioritizes clarity and speed of task completion, ensuring that complex data sets remain legible and actionable for professional users.

## Colors

The palette is anchored by a vibrant Indigo primary, serving as the main interactive signal. To elevate the enterprise feel, the neutral palette utilizes deep Navy tones rather than pure greys, providing a richer, more premium depth.

### Dark Mode Strategy
The interface utilizes a "Surface Elevation" model for dark mode. Backgrounds use the deepest navy (`#020617`), while containers and cards use progressive steps of Indigo-tinted slate. 

- **Primary:** Indigo (#6366f1) — Used for primary actions, active states, and focus indicators.
- **Secondary:** Sky (#38bdf8) — Used for information accents and secondary data visualizations.
- **Surface L1:** `#020617` (Deepest Navy - Background)
- **Surface L2:** `#0f172a` (Default Container)
- **Surface L3:** `#1e293b` (Elevated Elements)
- **Status:** Standardized Success (Emerald), Warning (Amber), and Error (Rose) tones, optimized for legibility against dark navy backgrounds.

## Typography

This design system employs a multi-font strategy to differentiate content types. **Hanken Grotesk** is used for headlines to provide a sharp, contemporary professional feel. **Inter** is the workhorse for all body and UI copy, chosen for its exceptional legibility in dense enterprise layouts. **JetBrains Mono** is utilized for metadata, timestamps, and status labels to evoke a sense of technical precision and biometric data accuracy.

Weight usage is disciplined: Semi-bold (600) for hierarchy, Regular (400) for readability. Letter spacing is slightly tightened on large headings to maintain visual density.

## Layout & Spacing

The layout follows a **Fluid Grid** model with strict adherence to an 8px base unit (with a 4px sub-unit for tight components). 

- **Desktop:** 12-column grid, 1440px max-width, center-aligned. Content utilizes broad margins to focus attention.
- **Tablet:** 8-column grid, 24px margins.
- **Mobile:** 4-column grid, 16px margins.

Spacing between functional groups should use larger increments (32px, 48px, 64px) to create clear sectioning without relying on heavy borders. Internal component padding should remain tight (8px, 12px, 16px) to maximize data density on dashboard views.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Low-Contrast Outlines**. 

In the dark theme, depth is not conveyed through heavy black shadows, but through subtle luminosity shifts. Higher elevation elements have a lighter background fill.

- **Level 0 (Base):** `#020617` (Global Background)
- **Level 1 (Cards/Sidebar):** `#0f172a` background with a 1px border of `rgba(255, 255, 255, 0.05)`.
- **Level 2 (Modals/Popovers):** `#1e293b` background with a subtle ambient glow (0px 8px 24px rgba(0, 0, 0, 0.5)).

Interactive elements like buttons use a slight inner-glow (stroke) on hover to simulate tactile feedback rather than physical movement.

## Shapes

The design system adopts a **Soft** shape language. This provides a modern touch while maintaining the structural rigidity expected of professional software.

- **Components (Buttons, Inputs):** 4px (`0.25rem`) corner radius.
- **Containers (Cards, Modals):** 8px (`0.5rem`) corner radius.
- **Status Indicators:** Fully rounded/pill-shaped for immediate distinction from interactive buttons.

Consistent corner radii ensure that even when nested, the UI feels architecturally sound.

## Components

### Buttons
- **Primary:** Solid Indigo fill, White text. 4px radius.
- **Secondary:** Transparent fill, 1px Navy-400 border, White text.
- **Ghost:** Transparent background, Indigo text. Used for low-priority actions in headers.

### Input Fields
Inputs use a deep navy background (`#020617`) with a 1px border. Focus state triggers a 1px Indigo border and a soft Indigo outer glow. Labels use the `label-sm` (Mono) style above the field.

### Data Tables
Tables are the core of the enterprise experience. Use a zebra-stripe pattern with Level 1 and Level 2 surfaces. Headers must be "Sticky" and use the `label-md` typography style for clarity.

### Chips & Badges
Used for status (e.g., "Active", "Clocked Out"). These utilize a low-opacity fill of the status color (e.g., 10% Green) with high-contrast text for maximum legibility without being distracting.

### Cards
Cards are the primary container for dashboard widgets. They should have a 1px border and no box-shadow, relying on the value difference between the card and the page background to define their bounds.