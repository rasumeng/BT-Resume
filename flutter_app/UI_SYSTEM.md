# Beyond The Resume (BTF) - Flutter UI Design System & Screens

This document outlines the complete UI implementation for the BTF-Resume Flutter application, featuring a modern dark theme with gold accents.

## 📁 Project Structure

```
lib/
├── constants/
│   ├── colors.dart           # Complete color palette
│   └── typography.dart       # Typography system
├── widgets/
│   ├── buttons/
│   │   ├── primary_button.dart      # Gold gradient buttons
│   │   └── secondary_button.dart    # Bordered buttons
│   ├── cards/
│   │   └── app_card.dart            # Reusable card component
│   ├── headers/
│   │   └── panel_header.dart        # Panel headers with gradient
│   ├── inputs/
│   │   └── custom_input_field.dart  # Custom input fields
│   ├── states/
│   │   └── empty_state.dart         # Empty state placeholder
│   ├── custom_scroll_bar.dart       # Custom scrollbar
│   ├── intensity_button.dart        # Intensity selector buttons
│   ├── list_panel_item.dart         # List item component
│   └── score_card.dart              # Score display card
├── screens/
│   ├── my_resumes_screen.dart       # Screen 1: View & Grade
│   ├── polish_screen.dart           # Screen 2: Polish
│   ├── tailor_screen.dart           # Screen 3: Tailor
│   └── experience_screen.dart       # Screen 4: Experience
└── main.dart                         # App entry & tabbed interface
```

## 🎨 Design System

### Color Palette (`lib/constants/colors.dart`)

```dart
// Primary Colors
AppColors.darkPrimary = #1a1a2e    // Main background
AppColors.darkSecondary = #16213e  // Secondary background
AppColors.dark2 = #2d2d4a          // Card/input background
AppColors.dark3 = #3a3a54          // Hover states
AppColors.dark4 = #4a4a64          // Borders

// Accents
AppColors.gold = #c9a84c           // Primary accent
AppColors.goldHover = #d4b85f      // Hover state
AppColors.cream = #f5f5f5          // Primary text

// Status Colors
AppColors.errorRed = #e74c3c       // Error states
AppColors.warningOrange = #f39c12  // Warnings
AppColors.successGreen = #27ae60   // Success

// Gradients
AppColors.goldGradient             // Gold gradient
AppColors.panelHeaderGradient      // Panel header gradient
```

### Typography (`lib/constants/typography.dart`)

| Style | Size | Weight | Color | Use Case |
|-------|------|--------|-------|----------|
| `headingPageTitle` | 32px | Bold | Cream | Page titles |
| `headingSectionTitle` | 16px | Bold | Gold | Section headers (uppercase) |
| `headingCardTitle` | 14px | Bold | Cream | Card titles |
| `bodyLarge` | 14px | 500 | Cream | Primary body text |
| `bodyNormal` | 12px | 400 | Secondary | Secondary text |
| `bodySmall` | 11px | 400 | Tertiary | Tertiary text |
| `labelText` | 11px | Bold | Gold | Labels (uppercase) |
| `scoreDisplay` | 24px | Bold | Gold | Score numbers |
| `monospace` | 12px | 400 | Cream | Code/resume text |

## 🧩 Reusable Components

### 1. PrimaryButton
**File**: `lib/widgets/buttons/primary_button.dart`
- Gold gradient background
- Hover effect: `translateY(-2px)` with shadow
- Smooth transitions (0.3s)
- Border radius: 8px
- Loading state support

### 2. SecondaryButton
**File**: `lib/widgets/buttons/secondary_button.dart`
- Transparent with gold border
- Hover: Fill with semi-transparent gold
- Smooth transitions
- Loading state support

### 3. AppCard
**File**: `lib/widgets/cards/app_card.dart`
- Dark2 background with dark4 border
- Hover: `translateX(4px)` + gold border
- Active state: Gold gradient background
- Customizable padding & border radius
- Optional click handler

### 4. PanelHeader
**File**: `lib/widgets/headers/panel_header.dart`
- Gradient background (dark2 → dark3)
- Gold title with uppercase + letter-spacing
- Gold border bottom
- Padding: 18-20px
- Optional trailing action

### 5. EmptyState
**File**: `lib/widgets/states/empty_state.dart`
- Centered layout
- Large icon (48px, 50% opacity)
- Primary message (bold)
- Secondary hint text (dim)
- Customizable icon size

### 6. ScoreCard
**File**: `lib/widgets/score_card.dart`
- 2x2 grid item
- Large score number (24px, bold, gold)
- Label below (11px, dim)
- "/10" suffix
- Hover effects (border + background change)

### 7. ListPanelItem
**File**: `lib/widgets/list_panel_item.dart`
- Selectable card list item
- Title + optional subtitle
- Active/selected state styling
- Optional delete button (red on hover)
- Truncated text handling

### 8. CustomInputField
**File**: `lib/widgets/inputs/custom_input_field.dart`
- Dark2 background with dark4 border
- Focus: Gold border + shadow
- Multiline support
- Custom placeholder text
- Label above field

### 9. IntensityButton
**File**: `lib/widgets/intensity_button.dart`
- Icon + label button
- Selected/unselected states
- Color-coded (green/orange/red)
- Smooth transitions

### 10. CustomScrollBar
**File**: `lib/widgets/custom_scroll_bar.dart`
- 6px width
- Dark4 color
- Custom styling

## 📱 Four Main Screens

### Screen 1: My Resumes (View & Grade)
**File**: `lib/screens/my_resumes_screen.dart`

**Layout**: 30/70 split

**Left Panel (30%)**:
- PanelHeader: "📄 Your Resumes"
- Scrollable list of resumes (ListPanelItem)
- Upload section (📁 Upload Resume, 📂 Manage Folder buttons)
- PanelHeader: "⭐ Grade & Score"
- 2x2 score grid (Overall, Format, Content, Impact) or empty state
- ✨ Grade Resume button

**Right Panel (70%)**:
- PanelHeader: "👁️ Preview"
- Scrollable resume text display
- Empty state when no resume selected

### Screen 2: Polish Resume
**File**: `lib/screens/polish_screen.dart`

**Layout**: 30/70 split

**Left Panel (30%)**:
- PanelHeader: "📄 Resumes"
- Scrollable resume list
- Section: "Polishing Intensity:"
  - 🟢 Light button
  - 🟡 Medium button (default active)
  - 🔴 Aggressive button
- ✨ Polish Resume button

**Right Panel (70%)**:
- **Top**: 50/50 split with vertical divider
  - Left: "📄 Original Resume" (scrollable)
  - Right: "✨ Polished Resume" (scrollable)
- **Bottom**: "📋 Changes Made"
  - List with ✓ checkmark icons (gold)
  - Scrollable list of changes

### Screen 3: Tailor Resume
**File**: `lib/screens/tailor_screen.dart`

**Layout**: 30/70 split

**Left Panel (30%)**:
- PanelHeader: "📄 Resumes"
- Scrollable resume list
- "Job Position" text input
- "Job Description" textarea (multiline)
- 🎯 Tailor Resume button

**Right Panel (70%)**:
- **Top**: 50/50 split with vertical divider
  - Left: "📄 Original Resume" (scrollable)
  - Right: "🎯 Tailored Resume" (scrollable)
- **Bottom**: "📋 Tailoring Summary"
  - Explanation text with checkmarks
  - Action buttons:
    - 💾 Replace Original (primary)
    - 💾 Save As (secondary)

### Screen 4: Experience
**File**: `lib/screens/experience_screen.dart`

**Layout**: 50/50 split with vertical divider

**Left Panel (50%)**:
- PanelHeader: "⚡ Experience Input"
- "Experience Details" textarea (monospace, 10 lines)
- "Job Section" text input
- 🚀 Generate Bullets button
- Pro tip box

**Right Panel (50%)**:
- PanelHeader: "📋 Generated Bullets"
- List of generated bullets:
  - Left gold border (3px)
  - ✓ checkmark icon (gold)
  - Bullet text
  - Scrollable
- Loading spinner (while generating)
- Empty state (no bullets yet)
- Bottom: 📋 Copy All button

## 🎭 Interactions & Animations

### Smooth Transitions
- All buttons: 0.3s ease transitions
- Cards: 0.3s ease transform on hover
- Input fields: Instant focus change with gold border + shadow

### Hover Effects
- **PrimaryButton**: `translateY(-2px)` + enhanced shadow
- **SecondaryButton**: Background fill with gold opacity
- **AppCard**: `translateX(4px)` + gold border
- **ListPanelItem**: Background color change
- **ScoreCard**: Background lightening + border color change
- **IntensityButton**: Gradient background fill

### States
- **Active/Selected**: Gold border or gradient background
- **Loading**: CircularProgressIndicator (gold color)
- **Error**: Red accent colors
- **Success**: Green accent colors
- **Disabled**: Reduced opacity, no hover effects

## 🔄 Tab Navigation

Main app includes 4 tabs:
1. **📄 MY RESUMES** - View and grade resumes
2. **✨ POLISH** - Polish resume with intensity options
3. **🎯 TAILOR** - Tailor to job descriptions
4. **⚡ EXPERIENCE** - Generate bullet points

Tab bar features:
- Gold underline indicator
- Uppercase labels
- Smooth transitions between tabs
- All screens display in full width

## 🚀 Getting Started

1. **Build the app**:
   ```bash
   cd flutter_app
   flutter pub get
   flutter build windows
   ```

2. **Run the app**:
   ```bash
   flutter run -d windows
   ```

3. **Hot reload** (during development):
   ```bash
   Press 'r' in the terminal
   ```

## 📐 Responsive Design

All components are responsive and work well with:
- Large desktop screens (1920x1080+)
- Medium monitors (1366x768)
- Custom window resizing

The layout uses Flutter's Row/Column with Expanded widgets to maintain proper proportions and spacing.

## 🎯 Best Practices Implemented

✅ **Code Organization**: Separated by concern (colors, typography, widgets, screens)
✅ **Reusability**: Highly reusable components with customization options
✅ **Consistency**: Unified design system across all screens
✅ **Performance**: Minimal rebuilds, efficient list rendering with CustomScrollBar
✅ **Accessibility**: Proper color contrast, readable typography, clear visual hierarchy
✅ **Animation**: Smooth 0.3s transitions on all interactive elements
✅ **Error Handling**: EmptyState components for missing data
✅ **User Feedback**: Toast notifications (SnackBar) for actions
✅ **Professional**: Enterprise-grade UI with modern design patterns

## 📝 Notes

- All screens use mock data by default for demonstration
- Integration with backend API would replace mock data with real data
- TabController manages the 4-tab navigation
- Each screen is a StatefulWidget for state management
- No external state management library (Provider/GetX) required for current implementation
- Can easily be extended with Provider or GetX for more complex state management
