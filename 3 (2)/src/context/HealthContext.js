import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const HealthContext = createContext(null);

// All state is persisted on-device under this key, so the app works fully
// offline and data survives restarts. Demo data is seeded once on first
// launch only.
const STORAGE_KEY = '@health_monitor/state/v1';

// ── Seed data generator ──────────────────────────────────────────────────────
function generateRecords() {
  const base = new Date('2026-06-21');
  const rows = [];
  let w = 74.2, sys = 122, dia = 80, hr = 73;
  let steps = 8200, sleep = 7.1, spo2 = 98, water = 2.1;

  for (let i = 59; i >= 0; i--) {
    const d = new Date(base);
    d.setDate(d.getDate() - i);

    w     = +Math.max(70.0, Math.min(78.0, w     + (Math.random() - 0.53) * 0.35)).toFixed(1);
    sys   = Math.round(Math.max(108, Math.min(138, sys   + (Math.random() - 0.5)  * 5)));
    dia   = Math.round(Math.max(68,  Math.min(90,  dia   + (Math.random() - 0.5)  * 4)));
    hr    = Math.round(Math.max(57,  Math.min(93,  hr    + (Math.random() - 0.5)  * 7)));
    steps = Math.round(Math.max(3500, Math.min(14000, steps + (Math.random() - 0.5) * 2400)));
    sleep = +Math.max(4.5, Math.min(9.5, sleep + (Math.random() - 0.5) * 1.2)).toFixed(1);
    spo2  = Math.round(Math.max(94, Math.min(100, spo2 + (Math.random() - 0.5) * 1)));
    water = +Math.max(0.8, Math.min(3.5, water + (Math.random() - 0.5) * 0.5)).toFixed(1);

    rows.push({
      id: `seed-${i}`,
      date: d.toISOString(),
      weight: w, systolic: sys, diastolic: dia, heartRate: hr,
      steps, sleep, spO2: spo2, water,
      notes: i === 0 ? 'Feeling great after morning run'
           : i === 5  ? 'Light yoga session'
           : i === 12 ? 'Skipped workout, feeling tired'
           : i === 20 ? '5K run — new personal best!'
           : i === 35 ? 'BP a bit high, less salt today'
           : i === 48 ? 'Great night sleep, felt energised'
           : '',
    });
  }
  return rows;
}

const INITIAL_RECORDS = generateRecords();

const INITIAL_GOALS = [
  {
    id: 'g1', type: 'weight', title: 'Lose 5 kg',
    target: 70, current: 72.5, unit: 'kg',
    deadline: '2026-08-30', status: 'on_track', achieved: false,
  },
  {
    id: 'g2', type: 'bp', title: 'Lower BP to 120/80',
    targetSys: 120, targetDia: 80, currentSys: 118, currentDia: 76,
    deadline: '2026-07-15', status: 'on_track', achieved: false,
  },
  {
    id: 'g3', type: 'steps', title: '10,000 Steps Daily',
    target: 10000, current: 8200, unit: 'steps',
    deadline: '2026-07-31', status: 'watch', achieved: false,
  },
];

const INITIAL_NOTIFICATIONS = [
  { id: 'n1', icon: 'alert-circle', color: '#F59E0B', title: 'BP Slightly Elevated', body: 'Your reading of 127/83 is above normal. Consider rest and hydration.', time: '2h ago', read: false },
  { id: 'n2', icon: 'footsteps',    color: '#00B894', title: 'Step Goal Reached!',  body: 'You hit 10,200 steps yesterday. Keep up the great work!',         time: '1d ago', read: false },
  { id: 'n3', icon: 'moon',         color: '#3B82F6', title: 'Sleep Summary',       body: 'You averaged 7.3 hrs of sleep this week. Aim for 7–9 hrs.',        time: '2d ago', read: true  },
  { id: 'n4', icon: 'water',        color: '#06B6D4', title: 'Hydration Reminder',  body: "You're at 1.4 L today. Try to reach your 2.5 L goal.",            time: '3d ago', read: true  },
  { id: 'n5', icon: 'heart',        color: '#00B894', title: 'Heart Rate Normal',   body: 'Resting HR of 69 bpm — excellent cardiovascular health.',          time: '4d ago', read: true  },
];

// ── Status helpers ────────────────────────────────────────────────────────────
export function getBPStatus(sys, dia) {
  if (!sys || !dia) return null;
  const s = parseInt(sys, 10), d = parseInt(dia, 10);
  if (s >= 140 || d >= 90) return 'high';
  if (s >= 120 || d >= 80) return 'elevated';
  return 'normal';
}
export function getHRStatus(hr) {
  if (!hr && hr !== 0) return null;
  const h = parseInt(hr, 10);
  if (isNaN(h) || h === 0) return null;
  return (h < 60 || h > 100) ? 'abnormal' : 'normal';
}
export function getSpO2Status(spo2) {
  const v = parseFloat(spo2);
  if (v >= 97) return 'normal';
  if (v >= 95) return 'low';
  return 'critical';
}
export function getSleepStatus(hrs) {
  const v = parseFloat(hrs);
  if (v >= 7 && v <= 9) return 'good';
  if (v >= 6 || v <= 9.5) return 'fair';
  return 'poor';
}
export function getOverallStatus(record) {
  const bp = getBPStatus(record.systolic, record.diastolic);
  const hr = getHRStatus(record.heartRate);
  if (bp === 'high' || hr === 'abnormal') return 'alert';
  if (bp === 'elevated') return 'watch';
  return 'good';
}

// ── Provider ──────────────────────────────────────────────────────────────────
const INITIAL_REMINDERS = [
  { id: 'r1', label: 'Morning Weigh-in',    time: '7:00 AM', enabled: true },
  { id: 'r2', label: 'Medication Reminder', time: '9:00 PM', enabled: true },
  { id: 'r3', label: 'Hydration Check',     time: '2:00 PM', enabled: false },
];

export function HealthProvider({ children }) {
  const [records, setRecords]           = useState(INITIAL_RECORDS);
  const [goals, setGoals]               = useState(INITIAL_GOALS);
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const [user]    = useState({ name: 'Henry Ejikeme', email: 'h.ejikeme@email.com', age: 32, height: '1.78 m' });
  const [streak]  = useState(21);
  const [reminders, setReminders] = useState(INITIAL_REMINDERS);
  const [hydrated, setHydrated] = useState(false);
  const saveTimer = useRef(null);

  // Load persisted state once on mount; fall back to the seed data on
  // first launch (or if storage is unreadable).
  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (raw) {
          const saved = JSON.parse(raw);
          if (Array.isArray(saved.records))       setRecords(saved.records);
          if (Array.isArray(saved.goals))         setGoals(saved.goals);
          if (Array.isArray(saved.notifications)) setNotifications(saved.notifications);
          if (Array.isArray(saved.reminders))     setReminders(saved.reminders);
        }
      } catch (e) {
        // Corrupt or unreadable storage: keep in-memory defaults.
      } finally {
        setHydrated(true);
      }
    })();
  }, []);

  // Persist on every change (debounced), but never before hydration —
  // otherwise the seed data would overwrite the user's saved state.
  useEffect(() => {
    if (!hydrated) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      AsyncStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ records, goals, notifications, reminders }),
      ).catch(() => {});
    }, 250);
    return () => clearTimeout(saveTimer.current);
  }, [hydrated, records, goals, notifications, reminders]);

  const addRecord = (entry) => {
    setRecords((prev) => [{
      id: Date.now().toString(),
      date: new Date().toISOString(),
      ...entry,
    }, ...prev]);
  };

  const addGoal = (goal) => {
    setGoals((prev) => [{
      id: Date.now().toString(),
      ...goal, status: 'on_track', achieved: false,
    }, ...prev]);
  };

  const toggleReminder = (id) =>
    setReminders((prev) => prev.map((r) => r.id === id ? { ...r, enabled: !r.enabled } : r));

  const addReminder = (reminder) =>
    setReminders((prev) => [...prev, { id: Date.now().toString(), ...reminder, enabled: true }]);

  const markNotificationsRead = () =>
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));

  const latest  = records[0] || {};
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <HealthContext.Provider value={{
      records, goals, user, streak, reminders, latest,
      notifications, unreadCount,
      addRecord, addGoal, toggleReminder, addReminder, markNotificationsRead,
    }}>
      {children}
    </HealthContext.Provider>
  );
}

export function useHealth() {
  const ctx = useContext(HealthContext);
  if (!ctx) throw new Error('useHealth must be used within HealthProvider');
  return ctx;
}
