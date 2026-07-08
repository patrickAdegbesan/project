# Personal Health Monitor

A mobile health tracking application built with React Native (Expo) that helps users log, visualise, and understand their daily health vitals.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Features](#features)
4. [App Architecture](#app-architecture)
5. [End-to-End Data Flow](#end-to-end-data-flow)
6. [Screen Walkthrough](#screen-walkthrough)
7. [Health Status Logic](#health-status-logic)
8. [Smart Watch Integration](#smart-watch-integration)
9. [Getting Started](#getting-started)

---

## Overview

Personal Health Monitor is a cross-platform mobile app (iOS & Android) that allows users to:

- Log daily health vitals: weight, blood pressure, heart rate, steps, sleep, SpO₂, and water intake
- View a real-time Overall Health Status based on clinical thresholds
- Track trends over time through interactive charts
- Set and monitor personal health goals
- Connect a smartwatch (Apple Watch, Samsung, Garmin, Fitbit) to auto-sync data
- Receive contextual health notifications and reminders

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React Native 0.85 + Expo SDK 56 |
| Navigation | React Navigation 7 (Native Stack + Bottom Tabs) |
| State Management | React Context API (`HealthContext`, `ThemeContext`) |
| Charts | react-native-svg (custom MiniLineChart component) |
| Gradients | expo-linear-gradient |
| Icons | @expo/vector-icons (Ionicons) |
| Styling | React Native StyleSheet (no third-party CSS lib) |
| Build | EAS Build (Expo Application Services) |
| Package Manager | Yarn 1.22 |

---

## Features

### Core
- **Health Logging** — Log weight, BP, heart rate, steps, sleep duration, SpO₂, and water intake with live inline feedback
- **Overall Health Status** — Calculated status badge (`Good` / `Watch` / `Alert`) shown on the home screen based on latest vitals
- **Weight Trend Chart** — 14-day line chart of weight history
- **Recent Activity Feed** — Scrollable list of past records with per-record status badges

### Analytics
- **Trends Screen** — 7-day and 30-day charts for all vitals, with min/max/average summaries
- **Goals Screen** — Create and track health goals (weight, BP, steps, etc.) with progress indicators and deadline tracking

### Smart Watch (new)
- **Device Pairing** — Choose from Apple Watch, Samsung Galaxy Watch, Garmin, or Fitbit; animated Bluetooth pairing flow
- **Live Metrics Panel** — View synced heart rate, SpO₂, steps, sleep, and water in one place
- **One-Tap Sync** — Push watch data directly into the health record history

### UX
- **Dark Mode** — Full dark/light theme toggle via `ThemeContext`
- **Notifications Panel** — In-app notification centre with unread badge counter
- **Reminders** — Configurable daily reminders for weigh-ins, medication, and hydration
- **21-Day Streak** — Motivational logging streak displayed on the home screen

---

## App Architecture

```
App.js
 └── HealthProvider (HealthContext)
      └── ThemeProvider (ThemeContext)
           └── AppNavigator
                ├── Stack: Login
                ├── Stack: Main (Bottom Tabs)
                │    ├── Tab: Home
                │    ├── Tab: Trends
                │    ├── Tab: Log (LogHealth)
                │    ├── Tab: Goals
                │    └── Tab: Profile
                └── Stack: Watch (full-screen modal-style)
```

### Key Files

| File | Purpose |
|---|---|
| `src/context/HealthContext.js` | Global state — records, goals, notifications, user, status logic |
| `src/context/ThemeContext.js` | Theme toggle and dynamic colour tokens |
| `src/navigation/AppNavigator.js` | Stack + Tab navigator setup |
| `src/screens/HomeScreen.js` | Dashboard — vitals summary, status card, activity grid |
| `src/screens/LogHealthScreen.js` | Vital entry form with live BP/HR feedback |
| `src/screens/TrendsScreen.js` | Historical charts for all metrics |
| `src/screens/GoalsScreen.js` | Goal creation and progress tracking |
| `src/screens/WatchScreen.js` | Smartwatch pairing and data sync |
| `src/screens/ProfileScreen.js` | User info, reminders, theme toggle |
| `src/theme/index.js` | All colour tokens, typography, spacing, shadows |
| `src/components/MiniChart.js` | SVG-based line chart component |
| `src/components/StatusBadge.js` | Colour-coded status badge (`Good/Watch/Alert`) |

---

## Data Persistence & Offline Use

All state (records, goals, reminders, notifications) is persisted
on-device with AsyncStorage under the key `@health_monitor/state/v1`,
so your data survives app restarts. Demo data is seeded once on first
launch only; everything you log afterwards is kept. The app makes no
network requests — it works fully offline.

## Terminal Client

Every feature of the app is also available from the terminal:

```
node cli.js             # interactive menu
node cli.js dashboard   # print the dashboard and exit
```

The CLI covers the dashboard, logging vitals (with the same BP/HR/SpO₂
status logic and health notifications), history, ASCII trend charts,
goals, reminders and profile. Data is stored in `health-data.json`
next to the script. No dependencies and no network needed.

## End-to-End Data Flow

```
User taps "Log Today's Vitals"
         │
         ▼
  LogHealthScreen
  ─ User types weight, BP, heart rate, steps, sleep, SpO₂, water
  ─ Live inline feedback shown for BP and HR as user types
  ─ On "Save Record":
      ├── Empty fields → stored as null (not 0) to avoid false alerts
      └── addRecord() called → new entry prepended to records[]
                                        │
                                        ▼
                              HealthContext (in-memory state)
                              ─ records[] updated (latest record = records[0])
                              ─ latest alias re-computed
                                        │
                                        ▼
                              HomeScreen re-renders
                              ─ getOverallStatus(latest) re-evaluated
                              ─ Status card updates colour/icon/badge
                              ─ Vitals stat cards update values
                              ─ Today's Activity grid updates
                              ─ Recent Activity list prepends new row
```

### Health Status Calculation

```
getOverallStatus(record)
  ├── getBPStatus(systolic, diastolic)
  │    ├── null fields   → null  (not enough data)
  │    ├── sys≥140 or dia≥90 → 'high'
  │    ├── sys≥120 or dia≥80 → 'elevated'
  │    └── otherwise         → 'normal'
  │
  ├── getHRStatus(heartRate)
  │    ├── null/zero/NaN  → null  (field not logged — no penalty)
  │    ├── hr<60 or hr>100 → 'abnormal'
  │    └── otherwise       → 'normal'
  │
  ├── bp==='high' OR hr==='abnormal' → 'alert'  (red card)
  ├── bp==='elevated'                → 'watch'  (amber card)
  └── otherwise                     → 'good'   (green card)
```

---

## Screen Walkthrough

### 1. Login Screen
Entry point. User taps "Sign In" to proceed to the main dashboard. (Authentication is stubbed — ready for a real auth backend.)

### 2. Home Screen
The central dashboard:
- **Header** — Greeting, current date, notification bell (with unread count), avatar
- **Vitals Strip** — Horizontally scrollable cards: Weight, Blood Pressure, Heart Rate, Streak
- **Overall Health Status Card** — Colour-coded (green/amber/red) summary based on latest record; taps through to Trends
- **Log Today's Vitals CTA** — Quick-access button to the Log screen
- **Connect Smart Watch** — One-tap entry to the Watch screen
- **Today's Activity Grid** — Steps (with goal progress bar), Sleep, Water, SpO₂
- **Weight Trend Chart** — 14-day sparkline
- **Recent Activity** — Last 3 logged records with status badges

### 3. Log Health Screen
- Individual field cards for each metric
- Real-time BP colour feedback (Normal/Elevated/High) as the user types
- Real-time HR feedback (Normal/Abnormal)
- Empty fields are saved as `null` — they do not affect the Overall Health Status
- Success toast + auto-navigate back to Home on save

### 4. Trends Screen
- Selectable date range (7 / 14 / 30 days)
- Line charts for Weight, Blood Pressure (sys + dia), Heart Rate, Steps, Sleep
- Summary stats: min, max, average for each metric

### 5. Goals Screen
- Active goals with progress bars and deadline countdown
- Add new goals: weight target, BP target, daily steps target
- Status chips: On Track / Watch / Achieved

### 6. Watch Screen (New)
- **Step 1 – Select Device**: Choose Apple Watch, Samsung Galaxy Watch, Garmin, or Fitbit
- **Step 2 – Pairing**: Animated Bluetooth connection flow with progress bar
- **Step 3 – Connected**: Live metrics panel showing heart rate, SpO₂, steps, sleep, water with "Synced" badges after a sync; "Sync Now" pushes data into the health record history

### 7. Profile Screen
- User info (name, email, age, height)
- Configurable reminders (toggle on/off, add new)
- Dark / Light mode toggle
- App info and version

---

## Health Status Logic

The Overall Health Status uses clinical reference ranges:

| Metric | Normal | Watch | Alert |
|---|---|---|---|
| Blood Pressure | <120/80 mmHg | 120–139 / 80–89 mmHg | ≥140/90 mmHg |
| Heart Rate | 60–100 bpm | — | <60 or >100 bpm |
| SpO₂ | ≥97% | 95–96% | <95% |

**Key rule**: if a field is not logged (left blank), it is stored as `null` and treated as "no data" — it does **not** contribute a penalty to the status score. This prevents the status from falsely showing "Alert" when only partial data is entered.

---

## Smart Watch Integration

The Watch screen implements a full pairing UX flow:

1. **Device discovery** — User picks their wearable brand
2. **Capability preview** — Shows which metrics the device can sync
3. **Bluetooth pairing** — Animated connection flow (production builds would use `react-native-ble-plx` or platform health APIs)
4. **Data sync** — "Sync Now" reads the latest watch metrics and calls `addRecord()`, stamping data with the device name in the notes field
5. **Disconnect** — Returns to device selection, clearing pairing state

> **Production note**: Actual Bluetooth/health platform integration requires native modules. For Apple Health use `react-native-health`; for Google Fit / Health Connect use `react-native-google-fit` or the Health Connect API. The current implementation uses the in-memory health context and is architected so the sync step is a single function call to replace.

---

## Getting Started

### Prerequisites
- Node.js ≥ 18
- Yarn 1.22
- Expo CLI (`npm install -g expo`)
- Expo Go app on your phone (for development)

### Install & Run

```bash
# Install dependencies
yarn install

# Start the development server
yarn start

# Run on Android
yarn android

# Run on iOS
yarn ios
```

### Build (EAS)

```bash
# Install EAS CLI
npm install -g eas-cli

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

---

## Folder Structure

```
├── App.js                    # Root component (providers)
├── index.js                  # Expo entry point
├── app.json                  # Expo app config
├── eas.json                  # EAS build config
├── assets/                   # App icons and splash screen
└── src/
    ├── components/
    │   ├── Card.js
    │   ├── CircularProgress.js
    │   ├── Icon.js
    │   ├── MiniChart.js
    │   └── StatusBadge.js
    ├── context/
    │   ├── HealthContext.js   # Data, state, status helpers
    │   └── ThemeContext.js    # Dark/light theme
    ├── navigation/
    │   └── AppNavigator.js
    ├── screens/
    │   ├── HomeScreen.js
    │   ├── LogHealthScreen.js
    │   ├── TrendsScreen.js
    │   ├── GoalsScreen.js
    │   ├── WatchScreen.js     # Smart watch pairing & sync
    │   ├── ProfileScreen.js
    │   └── LoginScreen.js
    └── theme/
        └── index.js           # Colours, typography, spacing, shadows
```

---

*Built with React Native + Expo · Designed for health monitoring and presentation*
