---
name: Bio Attendance Identity
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#4f4632'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
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
  tertiary: '#555f6f'
  on-tertiary: '#ffffff'
  tertiary-container: '#c1cbde'
  on-tertiary-container: '#4c5665'
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
  tertiary-fixed: '#d9e3f6'
  tertiary-fixed-dim: '#bdc7d9'
  on-tertiary-fixed: '#121c2a'
  on-tertiary-fixed-variant: '#3d4756'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
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
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 20px
  margin: 24px
  container-max: 1440px
---

## Brand & Style

The design system is engineered for a high-fidelity AI Biometric Attendance System, prioritizing clarity, trust, and professional efficiency. It adopts a **Modern Corporate** aesthetic with a heavy emphasis on **Minimalism**. By utilizing a high-contrast foundation of pure white and deep charcoal, the interface directs focus toward critical biometric data and status indicators. 

The personality is authoritative yet accessible. It avoids unnecessary decorative elements, instead using "Golden Yellow" as a precise functional accent to guide the user's eye toward primary actions and active states. The emotional response should be one of reliability and technological sophistication, ensuring that administrators feel in control of complex data sets.

## Colors

The palette is anchored by a stark, professional background to ensure maximum legibility for data-dense screens.

- **Primary & Secondary Accents:** A dual-tone Golden Yellow is used exclusively for interactive elements and brand signaling. `#FFC107` serves as the primary action color, while `#FFD700` is reserved for highlights and status indicators.
- **Neutrals:** The background hierarchy uses `#FFFFFF` for main content areas and `#F8F9FA` (Off-white) for structural scaffolding, such as sidebars or striped table rows.
- **Typography & Borders:** High-contrast Dark Gray (`#1F2937`) ensures AA accessibility for all body text. Borders are kept thin and subtle using `#E5E7EB` to maintain a light, airy feel without losing structural definition.

## Typography

The design system utilizes **Inter** for its entire typographic scale. Inter's tall x-height and systematic spacing make it ideal for data-heavy corporate software where readability is paramount.

- **Headlines:** Use a bold weight with slight negative letter-spacing to create a strong visual anchor for page titles.
- **Body:** Standardized at 14px for density and 16px for long-form reading, ensuring clarity in logs and reports.
- **Labels:** Small caps or bolded weights are used for table headers and form labels to differentiate them from user-generated content.
- **Hierarchy:** Use color (Dark Gray vs. Muted Gray) alongside weight to establish clear information hierarchy.

## Layout & Spacing

This design system follows a **12-column Fixed Grid** model for desktop, transitioning to a fluid layout for mobile devices.

- **Grid:** On desktop, the content is contained within a 1440px max-width container. 
- **Rhythm:** A 4px baseline grid ensures consistent vertical rhythm. Use 16px (`md`) for standard padding within cards and 24px (`lg`) for section margins.
- **Responsive Behavior:** 
  - **Desktop (1024px+):** 12 columns, 20px gutters, 24px side margins.
  - **Tablet (768px - 1023px):** 8 columns, 16px gutters, 20px side margins.
  - **Mobile (Below 767px):** 4 columns, 16px gutters, 16px side margins. 
- **Sidebars:** Fixed at 280px on desktop to house the text-only navigation menu.

## Elevation & Depth

To maintain a clean, corporate feel, depth is communicated through **Tonal Layering** and **Subtle Ambient Shadows**.

- **Level 0 (Base):** Off-white (`#F8F9FA`) for the application background.
- **Level 1 (Surface):** Pure white (`#FFFFFF`) for cards and input fields. This creates a natural "lift" against the off-white background.
- **Shadows:** Use a single, highly-diffused shadow for cards: `0px 4px 12px rgba(0, 0, 0, 0.05)`. Avoid heavy or dark shadows to keep the UI light.
- **Interactive Depth:** On hover, interactive cards may transition to a slightly more pronounced shadow (`0px 8px 20px rgba(0, 0, 0, 0.08)`) or adopt a soft yellow background tint (`#FEF3C7`).

## Shapes

The shape language is "Rounded," balancing the strictness of corporate software with modern approachable aesthetics.

- **Cards:** Defined at 12px (`rounded-lg`) to soften the large data surfaces.
- **Buttons & Inputs:** Set at 8px to maintain a compact, professional look for interactive controls.
- **Highlight Elements:** Active states in the sidebar use a sharp 4px vertical bar on the left edge, contrasting with the rounded corners of the main containers.

## Components

- **Buttons:** 
  - *Primary:* Solid `#FFC107` fill with `#1F2937` text. 8px border radius.
  - *Secondary:* Transparent fill with `#E5E7EB` border and `#1F2937` text.
- **Input Fields:** Pure white background, `#E5E7EB` border. On focus, the border transitions to `#FFC107` with a 2px soft yellow glow.
- **Cards:** Use `#FFFFFF` background with a 12px radius. For high-priority alerts or highlighted biometric matches, add a 2px top border in `#FFD700`.
- **Navigation:** Sidebar menu items are text-only (`body-md`). The active item features a 4px wide `#FFC107` vertical border on the far left and a `#FEF3C7` background tint.
- **Tables:** Header rows use a light gray bottom border and bold labels. Data rows use alternating `#FFFFFF` and `#F8F9FA` backgrounds (striped) to improve horizontal tracking of employee records.
- **Chips/Badges:** Small, rounded-pill indicators for "Present" (Green tint), "Absent" (Red tint), or "Late" (Yellow tint), using a 12px font size.