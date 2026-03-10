# UI/UX Specification: Lyric Scroll

## Design Philosophy

Lyric Scroll prioritizes **readability** and **immersion**. The interface should fade into the background, letting the lyrics and music take center stage. Every design decision serves the goal of creating a seamless, distraction-free karaoke experience suitable for living rooms, parties, and personal listening.

## Display Modes

### 1. Scroll Mode (Default)

The primary viewing experience. Lyrics scroll vertically with the current line centered and highlighted.

```
         ┌─────────────────────────────────┐
         │                                 │
         │      previous line (dimmed)     │
         │                                 │
         │  ══► CURRENT LINE (bright) ◄══  │
         │                                 │
         │       next line (dimmed)        │
         │                                 │
         │      upcoming line (dimmed)     │
         │                                 │
         └─────────────────────────────────┘
```

**Behavior:**
- Current line is visually prominent (larger, brighter, possibly different color)
- 2-3 lines visible above and below current line
- Smooth scrolling animation (CSS transitions, 300ms ease-out)
- Word-by-word highlighting when enhanced LRC available

### 2. Page Mode

Shows a fixed number of lines, flipping to the next page when needed.

```
         ┌─────────────────────────────────┐
         │                                 │
         │   ══► Line 1 (current) ◄══      │
         │       Line 2                    │
         │       Line 3                    │
         │       Line 4                    │
         │                                 │
         │              ○ ○ ●              │
         │         (page indicator)        │
         └─────────────────────────────────┘
```

**Behavior:**
- Configurable lines per page (3-8, default 4)
- Page transitions with crossfade animation
- Current line highlighted within the page
- Optional page indicator dots at bottom

### 3. Focus Mode

Minimalist single-line display for maximum readability at distance.

```
         ┌─────────────────────────────────┐
         │                                 │
         │                                 │
         │                                 │
         │     THE CURRENT LYRIC LINE      │
         │                                 │
         │                                 │
         │                                 │
         └─────────────────────────────────┘
```

**Behavior:**
- Only current line visible
- Maximum font size
- Fade transition between lines (400ms)
- Optional subtle animation (gentle pulse, text glow)

## Visual Design

### Typography

| Element | Font | Weight | Size (Desktop) | Size (Mobile) |
|---------|------|--------|----------------|---------------|
| Current line | System Sans | Bold | 48px | 28px |
| Other lines | System Sans | Regular | 32px | 20px |
| Track info | System Sans | Light | 18px | 14px |
| Settings labels | System Sans | Regular | 16px | 14px |

**Font Stack:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

**User-adjustable sizes:**
- Small: 70% of base
- Medium: 100% of base (default)
- Large: 130% of base
- Extra Large: 160% of base

### Color Themes

#### Dark Theme (Default)
```css
--bg-primary: #0a0a0a;
--bg-secondary: #1a1a1a;
--text-primary: #ffffff;
--text-secondary: #888888;
--text-dimmed: #444444;
--accent: #4a9eff;
--accent-glow: rgba(74, 158, 255, 0.3);
```

#### Light Theme
```css
--bg-primary: #ffffff;
--bg-secondary: #f5f5f5;
--text-primary: #1a1a1a;
--text-secondary: #666666;
--text-dimmed: #cccccc;
--accent: #0066cc;
--accent-glow: rgba(0, 102, 204, 0.2);
```

#### OLED Theme (True Black)
```css
--bg-primary: #000000;
--bg-secondary: #0a0a0a;
--text-primary: #ffffff;
--text-secondary: #777777;
--text-dimmed: #333333;
--accent: #00ff88;
--accent-glow: rgba(0, 255, 136, 0.3);
```

### Current Line Highlight Styles

Users can choose how the current line is emphasized:

1. **Bright** (default) - Current line at full opacity, others dimmed
2. **Glow** - Subtle text-shadow glow effect on current line
3. **Underline** - Animated underline beneath current line
4. **Color** - Current line uses accent color

### Word-by-Word Highlighting

When enhanced LRC with word timing is available:

```
"I want to ████ the world"
          ▲
    word being sung (highlighted)
```

- Sung words transition from dimmed to bright
- Smooth color transition (150ms)
- Optional "karaoke wipe" effect (color fills left-to-right across word)

## Layout Specifications

### Main Display View

```
┌────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │                                                      │  │
│  │                                                      │  │
│  │                    LYRICS AREA                       │  │
│  │                   (full height)                      │  │
│  │                                                      │  │
│  │                                                      │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Track: Song Title - Artist Name          ⚙️ Settings │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Spacing:**
- Lyrics area: 100vh - 60px (info bar height)
- Padding: 5% horizontal, 10% vertical
- Info bar: Fixed bottom, 60px height

### Settings Panel (Overlay)

```
┌────────────────────────────────────────────────────────────┐
│                                              ✕ Close       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DISPLAY                                             │  │
│  │  ────────                                            │  │
│  │  Mode:     [Scroll ▼]                                │  │
│  │  Theme:    [Dark ▼]                                  │  │
│  │  Font:     [──●────] Large                           │  │
│  │                                                      │  │
│  │  SYNC                                                │  │
│  │  ────                                                │  │
│  │  Offset:   [────●──] +200ms                          │  │
│  │            [-] [Test] [+]                            │  │
│  │                                                      │  │
│  │  HIGHLIGHT                                           │  │
│  │  ─────────                                           │  │
│  │  Style:    ○ Bright  ● Glow  ○ Underline  ○ Color   │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Behavior:**
- Slides in from right (300ms ease-out)
- Semi-transparent backdrop
- Settings persist to localStorage and sync to backend
- Changes apply immediately (live preview)

## States and Transitions

### Loading State

```
         ┌─────────────────────────────────┐
         │                                 │
         │                                 │
         │            ◠ ◠ ◠               │
         │       Loading lyrics...         │
         │                                 │
         │   "Song Title" by Artist        │
         │                                 │
         └─────────────────────────────────┘
```

### No Lyrics Found

```
         ┌─────────────────────────────────┐
         │                                 │
         │                                 │
         │             ♪ ♫                 │
         │                                 │
         │     No lyrics available         │
         │                                 │
         │   "Song Title" by Artist        │
         │                                 │
         └─────────────────────────────────┘
```

### Idle State (Nothing Playing)

```
         ┌─────────────────────────────────┐
         │                                 │
         │                                 │
         │                                 │
         │         Lyric Scroll            │
         │    Waiting for music...         │
         │                                 │
         │                                 │
         │                                 │
         └─────────────────────────────────┘
```

### Paused State

- Lyrics remain visible at current position
- Subtle "paused" indicator (dimmed text or pause icon)
- Resume continues from paused position

## Animations

### Scroll Animation
- **Trigger:** New line becomes current
- **Duration:** 300ms
- **Easing:** ease-out
- **Property:** transform: translateY()

### Fade Transitions
- **Page flip:** 400ms crossfade
- **Focus mode line change:** 400ms fade
- **Settings panel:** 300ms slide + fade

### Word Highlight
- **Duration:** 150ms
- **Property:** color, opacity
- **Easing:** linear (for precise sync)

### Idle Pulse
- **Duration:** 2000ms
- **Property:** opacity (0.5 → 1 → 0.5)
- **Easing:** ease-in-out

## Responsive Behavior

### Breakpoints

| Breakpoint | Width | Adjustments |
|------------|-------|-------------|
| Desktop | > 1024px | Full layout, largest text |
| Tablet | 768-1024px | Reduced padding, medium text |
| Mobile | < 768px | Compact layout, smallest text |

### Touch Interactions

- **Tap anywhere:** Toggle info bar visibility
- **Swipe up:** Open settings
- **Swipe down:** Close settings
- **Pinch:** Adjust font size (if supported)

### Landscape vs Portrait

- **Landscape:** Optimal for TV/monitor casting
- **Portrait:** Stack layout, info bar may move to top

## Accessibility

### Requirements

- Minimum contrast ratio: 4.5:1 (WCAG AA)
- Focus indicators for keyboard navigation
- Reduced motion option (disables animations)
- Screen reader: Announce current line changes

### Reduced Motion

When `prefers-reduced-motion` is set:
- Instant transitions (no animation)
- No pulse effects
- Static highlight (no wipe effect)

## Cast/Chromecast Considerations

- No interactive elements needed on cast display
- Info bar hidden during cast (full-screen lyrics)
- Settings controlled from source device
- High contrast default for TV viewing
- Overscan-safe margins (5% padding)

## Error States

### Connection Lost
```
⚠ Connection lost. Reconnecting...
```
- Auto-retry with exponential backoff
- Last known lyrics remain visible

### Media Player Unavailable
```
⚠ Media player not found
Check Home Assistant configuration
```

## Future Considerations (Not MVP)

- Album art background (blurred, low opacity)
- Color extraction from album art for dynamic theming
- Multi-language display (original + translation)
- Sing-along mode with microphone input visualization
- Party mode with confetti/effects on song end
