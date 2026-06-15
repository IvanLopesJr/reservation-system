# System Design Tokens — Sistema de Reservas

## Direction & Feel
Tech/Vibrante. Modern, energetic, and polished. Inspired by contemporary SaaS dashboards with bold indigo/rose contrast, gradient accents, and smooth micro-interactions.

## Palette
- **Primary (Indigo):** `#4f46e5` — vibrant, modern, tech foundation
- **Accent (Rose):** `#f43f5e` — warm contrast, energy, destructive actions
- **Warning (Amber):** `#f59e0b` — warnings, highlights
- **Success (Emerald):** `#10b981` — availability, confirmation
- **Info (Cyan):** `#06b6d4` — informational badges
- **Background (Slate-50):** `#f8fafc` — clean, cool-toned page canvas
- **Surface (White):** `#ffffff` — white cards with shadow depth
- **Controls (Slate-50):** `#f8fafc` — form control backgrounds

## Depth Strategy
**Shadow-based depth** with hover lift:
- Card: `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)`
- Card hover: `translateY(-2px)` + `box-shadow: 0 10px 25px rgba(79,70,229,0.10)`
- Dropdowns/modals: `--shadow-lg`
- Buttons: `scale(1.02)` on hover, `scale(0.97)` on active

## Spacing
- **Base unit:** `4px`
- Scale: `4px → 8px → 12px → 16px → 20px → 24px → 32px`

## Border Radius
- Controls/buttons: `6px`
- Cards: `10px`
- Badges: `999px` (pill)
- Icon circles: `12px`

## Typography
- **Font:** Inter (Google Fonts) with system-ui fallback
- **Text hierarchy:**
  - Primary: `var(--slate-900)` — body, headings
  - Secondary: `var(--slate-600)` — labels
  - Tertiary: `var(--slate-400)` — metadata
  - Muted: `var(--slate-300)` — disabled

## Animations

### Card Entrance
- `@keyframes fadeInUp` — 0.4s cubic-bezier(0.16, 1, 0.3, 1)
- Staggered via `.delay-1` through `.delay-8` (0.03s increments)

### Micro-interactions
- **Card hover:** `translateY(-2px)` with enhanced shadow (indigo tint)
- **Button hover:** `translateY(-1px)` + `scale(1.02)` + shadow
- **Button active:** `scale(0.97)`
- **Table row hover:** Left inset indigo border (`3px solid indigo`)
- **Dropdown items:** Indigo tint on hover

### Loading
- **Shimmer skeleton:** Linear gradient sweep over slate-100/slate-200
- **HTMX loading:** Card-shaped shimmer replaces content during fetch

### Alerts
- **Toast slide-in:** `slideInRight` 0.35s cubic-bezier(0.16, 1, 0.3, 1)

## Gradients
- **Primary gradient:** `linear-gradient(135deg, var(--app-primary), var(--app-secondary))` (dynamic from settings)
- **Rose gradient:** `linear-gradient(135deg, #f43f5e, #fb7185)`
- Used on: welcome hero cards, stat icon circles, primary buttons
- Login title: gradient text via `-webkit-background-clip: text`

## Key Component Patterns

### Cards
- White bg (`var(--surface-card)`), `1px solid var(--border-default)`, `--shadow-md`
- Hover: `translateY(-2px)` + `--shadow-hover`
- `.card-hover-lift` class for explicit lift control

### Buttons
- Primary: gradient bg, no border, white text
- Hover: lift + enhanced shadow with indigo tint
- Active: `scale(0.97)`
- Outline: indigo border, fills with gradient on hover

### Form Controls
- Background: `var(--control-bg)`, focus: `var(--surface-raised)`
- Focus ring: `3px rgba(79, 70, 229, 0.10)`
- Checkbox checked: indigo

### Tables
- Header: uppercase, 0.7rem, `0.06em` letter-spacing
- Row hover: subtle indigo tint + left edge accent

### Badges
- Pill shape (`border-radius: 999px`)
- Semantic: success=emerald, warning=amber, danger=rose, info=cyan

### Position/Parking Cards (Signature — "Desk Lamp")
- **Available:** Emerald tint bg, green border, lift on hover
- **Selected:** Indigo border 2px + `box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15)` + lift
- **Occupied:** Slate-100 bg, muted, cursor not-allowed

### Icon Circles
- 48x48 or 36x36 rounded containers (12px/10px radius)
- Gradient backgrounds for primary/rose metrics

## Toast Notifications
- Fixed container at top-right (`position: fixed; z-index: 9999`)
- Stacked vertically with `gap: 0.5rem`
- Slide-in from right animation
- Auto-dismiss at 5s with Bootstrap Toast API
- Colored left border by type (emerald/rose/amber/cyan)

## Offcanvas Mobile Nav
- Large screens: standard navbar dropdowns
- Small screens (`d-lg-none`): offcanvas panel from right
- Offcanvas header with brand + close button
- Full link tree including admin section, password, and logout

## Real-time Form Validation
- `validation.js` validates on `blur` + subsequent `input` events
- `.is-valid` / `.is-invalid` classes control visual feedback
- Green check icon / red X icon as background images
- Inline `.feedback-valid` / `.feedback-invalid` text messages
- Server-side validation remains primary

## Skeleton Loading (HTMX)
- Shimmer skeleton replaces content during HTMX fetches
- Shimmer: linear gradient sweep on slate-100/slate-200
- Card, line, short, and shorter variants

## CSS Architecture
- **custom.css:** Design tokens + all component/animation styles
- **base.html:** Injects dynamic `--app-*` vars from SystemSettings
- **main.js:** Shimmer skeleton for HTMX loading, tooltip init
- **validation.js:** Real-time form field validation

## Removed Features
- **Dark Mode:** Removed due to performance impact (toggle, CSS overrides, theme.js)
- **hx-boost:** Removed due to performance impact (AJAX page transitions)

## Model Defaults (SystemSettings)
- `primary_color`: `#4f46e5` (was `#0d6efd`)
- `secondary_color`: `#f43f5e` (was `#6c757d`)
- `background_color`: `#f8fafc` (was `#f8f9fa`)
- `navbar_bg_color`: `#4f46e5` (was `#0d6efd`)
