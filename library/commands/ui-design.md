---
name: ui-design
description: Taqseem-inspired UI design system (Emerald primary, Deep Slate foundation, Tailwind tokens). Apply consistently across components.
applies_to: ["role:frontend", "role:fullstack"]
---

# UI Design Skill — Taqseem-Inspired Design System

You are building a frontend UI. Apply the design system below consistently across all components. The aesthetic is **professional, clean, and minimal** — Emerald green as the primary accent on a Deep Slate foundation, white card surfaces, soft muted backgrounds.

---

## Stack

- **Vite + React + TypeScript**
- **Tailwind CSS** with custom tokens (defined below)
- **shadcn/ui** for base components (Button, Card, Input, Label, Badge, etc.)
- **Lucide React** for all icons — never use emoji as icons in UI components

---

## Tailwind Config — Custom Tokens

Add this to your `tailwind.config.ts` under `theme.extend.colors`:

```ts
colors: {
  primary: {
    DEFAULT:      '#059669', // emerald-600
    hover:        '#047857', // emerald-700
    active:       '#065f46', // emerald-800
    soft:         '#d1fae5', // emerald-100
    softer:       '#ecfdf5', // emerald-50
    borderLight:  '#6ee7b7', // emerald-300
  },
  secondary: {
    DEFAULT:      '#1e293b', // slate-800
    hover:        '#334155', // slate-700
    active:       '#475569', // slate-600
    soft:         '#f1f5f9', // slate-100
    softer:       '#f8fafc', // slate-50
    borderLight:  '#e2e8f0', // slate-200
    borderSoft:   '#cbd5e1', // slate-300
    mutedText1:   '#475569', // slate-600
    mutedText2:   '#94a3b8', // slate-400
  },
  success: {
    DEFAULT:      '#16a34a', // green-600
    hover:        '#15803d', // green-700
    active:       '#166534', // green-800
    soft:         '#dcfce7', // green-100
    borderLight:  '#86efac', // green-300
  },
  warning: {
    DEFAULT:      '#d97706', // amber-600
    hover:        '#b45309', // amber-700
    active:       '#92400e', // amber-800
    soft:         '#fef3c7', // amber-100
  },
  error: {
    DEFAULT:      '#dc2626', // red-600
    hover:        '#b91c1c', // red-700
    active:       '#991b1b', // red-800
    soft:         '#fee2e2', // red-100
  },
  info: {
    DEFAULT:      '#2563eb', // blue-600
    hover:        '#1d4ed8', // blue-700
    soft:         '#dbeafe', // blue-100
  },
}
```

---

## Color Usage Rules

| Token | Use for |
|---|---|
| `primary` | CTA buttons, active states, links, focus rings, accents |
| `secondary` | Page titles, dark backgrounds, secondary buttons |
| `secondary-softer` | Page background (`min-h-screen bg-secondary-softer`) |
| `secondary-soft` | Table headers, disabled inputs, subtle fills |
| `secondary-borderLight` | Card borders, dividers, input borders |
| `secondary-mutedText1` | Sub-labels, table column headers |
| `secondary-mutedText2` | Captions, placeholders, helper text |
| `success/warning/error/info` | Status badges, alerts, semantic feedback only |

**Never** use raw Tailwind colors like `blue-500` or `gray-300` directly — always use the custom tokens above.

---

## Layout

```tsx
// Page shell
<div className="min-h-screen bg-secondary-softer">
  {/* Top nav */}
  <div className="bg-white border-b border-secondary-borderLight">
    <div className="max-w-7xl mx-auto px-8 py-4">
      {/* logo + nav */}
    </div>
  </div>

  {/* Content */}
  <div className="max-w-7xl mx-auto px-8 py-8 space-y-6">
    {/* Cards go here */}
  </div>
</div>
```

---

## Component Patterns

### Card
```tsx
<Card>
  <CardHeader>
    <CardTitle className="text-xl text-secondary flex items-center gap-2">
      <IconName className="h-5 w-5 text-primary" />
      Title
    </CardTitle>
    <CardDescription className="text-secondary-mutedText2">
      Subtitle or description
    </CardDescription>
  </CardHeader>
  <CardContent>
    {/* content */}
  </CardContent>
</Card>
```

### Buttons
```tsx
// Primary CTA
<Button className="bg-primary hover:bg-primary-hover active:bg-primary-active text-white">
  Save
</Button>

// Secondary
<Button variant="secondary" className="bg-secondary hover:bg-secondary-hover text-white">
  Cancel
</Button>

// Outline
<Button variant="outline" className="border-secondary-borderLight text-secondary">
  View
</Button>

// Destructive
<Button variant="destructive" className="bg-error hover:bg-error-hover">
  Delete
</Button>

// Ghost
<Button variant="ghost" className="text-secondary-mutedText1">
  Dismiss
</Button>
```

### Badges (status indicators)
```tsx
// Use these exact variants — all have soft bg + matching border + text
<Badge variant="default">Active</Badge>        // emerald
<Badge variant="secondary">Draft</Badge>       // slate
<Badge variant="success">Approved</Badge>      // green
<Badge variant="warning">Pending</Badge>       // amber
<Badge variant="destructive">Rejected</Badge>  // red
<Badge variant="outline">Archived</Badge>      // white + slate border
```

Badge cva config:
```ts
variant: {
  default:     'bg-primary/10 text-primary border border-primary/20',
  secondary:   'bg-secondary-soft text-secondary-mutedText1 border border-secondary-borderLight',
  destructive: 'bg-error/10 text-error border border-error/20',
  outline:     'bg-white text-secondary-mutedText1 border border-secondary-borderLight',
  success:     'bg-success/10 text-success border border-success/20',
  warning:     'bg-warning/10 text-warning border border-warning/20',
  info:        'bg-info/10 text-info border border-info/20',
}
```

### Input
```tsx
<div className="space-y-2">
  <Label className="text-sm font-medium text-secondary">Field Label</Label>
  <Input
    placeholder="Placeholder..."
    className="border-secondary-borderLight focus:border-primary focus:ring-primary"
  />
</div>

// Search input with icon
<div className="relative">
  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-mutedText2" />
  <Input placeholder="Search..." className="pl-10 border-secondary-borderLight" />
</div>

// Error state
<Input className="border-error focus:border-error focus:ring-error" />
<p className="text-xs text-error">Error message</p>
```

### Status / Alert Cards
```tsx
// Success
<div className="p-4 bg-success-soft border-2 border-success-borderLight rounded-lg">
  <div className="flex items-center gap-3">
    <div className="h-10 w-10 rounded-full bg-success flex items-center justify-center flex-shrink-0">
      <CheckCircle2 className="h-5 w-5 text-white" />
    </div>
    <div>
      <p className="text-sm font-bold text-success">Success Title</p>
      <p className="text-xs text-success-active">Subtitle</p>
    </div>
  </div>
</div>

// Warning — replace bg-success-soft → bg-warning-soft, border → border-warning/20, icon → AlertCircle, text → text-warning-hover
// Error   — replace with bg-error-soft, border-error/20, icon → XCircle, text → text-error
```

### Data Table
```tsx
<div className="border border-secondary-borderLight rounded-lg overflow-hidden">
  <table className="w-full">
    <thead className="bg-secondary-soft">
      <tr>
        <th className="px-4 py-3 text-left text-xs font-semibold text-secondary-mutedText1 uppercase tracking-wide">
          Column
        </th>
      </tr>
    </thead>
    <tbody className="bg-white divide-y divide-secondary-borderSoft">
      <tr className="hover:bg-secondary-softer">
        <td className="px-4 py-3 text-sm text-secondary">Value</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## Icons (Lucide React)

Always import from `lucide-react`. Common ones used in this system:

| Purpose | Icon |
|---|---|
| Success / confirmed | `CheckCircle2` |
| Warning / pending | `AlertCircle` |
| Error / rejected | `XCircle` |
| Info | `Info` |
| Search | `Search` |
| Settings | `Settings` |
| User | `User` |
| Dashboard / charts | `BarChart2` |
| Navigation | `ChevronRight`, `ChevronDown` |
| Actions | `Plus`, `Trash2`, `Pencil`, `Eye` |
| Close / dismiss | `X` |

Size conventions: `h-4 w-4` inline, `h-5 w-5` in buttons/badges, `h-6 w-6` section headers.

---

## Typography Scale

```
text-4xl font-bold text-secondary        → Page titles (H1)
text-[26px] font-semibold text-secondary → Section headers (H2)
text-xl font-semibold text-secondary     → Card titles (H3)
text-sm text-secondary-mutedText2        → Body / descriptions
text-xs text-secondary-mutedText2        → Captions, metadata, labels
text-xs uppercase tracking-wide         → Section divider labels
font-mono text-secondary-mutedText1      → IDs, codes, timestamps
```

---

## Spacing

Use Tailwind's 4px base unit. Standard gaps: `gap-2` (8px), `gap-3` (12px), `gap-4` (16px), `gap-6` (24px). Card padding: `p-4` or `p-6`. Page sections: `space-y-6` or `space-y-8`.

---

## Don'ts

- No raw hex values in JSX — use Tailwind tokens
- No emoji as UI icons — use Lucide
- No raw Tailwind colors (`blue-500`, `gray-300`) — use custom tokens
- No heavy shadows — use `border` + soft background instead
- No rounded-full on cards — use `rounded-lg`
