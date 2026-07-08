#!/usr/bin/env node
/**
 * Personal Health Monitor — Terminal client.
 *
 * Every feature of the mobile app, from the terminal: dashboard, logging
 * vitals, history, trends, goals, reminders and notifications. State is
 * persisted to ./health-data.json (the mobile app persists the same state
 * shape on-device with AsyncStorage). Fully offline; no dependencies.
 *
 * Usage:  node cli.js            interactive menu
 *         node cli.js dashboard  print dashboard and exit
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const DATA_FILE = path.join(__dirname, 'health-data.json');

// ── Status helpers (same thresholds as src/context/HealthContext.js) ────────
function getBPStatus(sys, dia) {
  if (!sys || !dia) return null;
  if (sys >= 140 || dia >= 90) return 'high';
  if (sys >= 120 || dia >= 80) return 'elevated';
  return 'normal';
}
function getHRStatus(hr) {
  if (!hr && hr !== 0) return null;
  return (hr < 60 || hr > 100) ? 'abnormal' : 'normal';
}
function getSpO2Status(spo2) {
  if (spo2 >= 97) return 'normal';
  if (spo2 >= 95) return 'low';
  return 'critical';
}
function getSleepStatus(hrs) {
  if (hrs >= 7 && hrs <= 9) return 'good';
  if (hrs >= 6 || hrs <= 9.5) return 'fair';
  return 'poor';
}
function getOverallStatus(r) {
  const bp = getBPStatus(r.systolic, r.diastolic);
  const hr = getHRStatus(r.heartRate);
  if (bp === 'high' || hr === 'abnormal') return 'alert';
  if (bp === 'elevated') return 'watch';
  return 'good';
}

// ── Persistence ──────────────────────────────────────────────────────────────
function defaultState() {
  return {
    user: { name: 'Henry Ejikeme', email: 'h.ejikeme@email.com', age: 32, height: '1.78 m' },
    records: [],
    goals: [],
    reminders: [
      { id: 'r1', label: 'Morning Weigh-in',    time: '7:00 AM', enabled: true },
      { id: 'r2', label: 'Medication Reminder', time: '9:00 PM', enabled: true },
      { id: 'r3', label: 'Hydration Check',     time: '2:00 PM', enabled: false },
    ],
    notifications: [],
  };
}

function load() {
  try {
    return { ...defaultState(), ...JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')) };
  } catch {
    return defaultState();
  }
}

function save(state) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(state, null, 2));
}

// ── Rendering helpers ────────────────────────────────────────────────────────
function sparkline(values) {
  const blocks = '▁▂▃▄▅▆▇█';
  const nums = values.filter((v) => typeof v === 'number' && !isNaN(v));
  if (!nums.length) return '(no data)';
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  return values.map((v) => {
    if (typeof v !== 'number' || isNaN(v)) return ' ';
    const idx = max === min ? 0 : Math.round(((v - min) / (max - min)) * (blocks.length - 1));
    return blocks[idx];
  }).join('');
}

function fmtDate(iso) {
  return new Date(iso).toISOString().slice(0, 10);
}

function pushNotification(state, icon, title, body) {
  state.notifications.unshift({
    id: Date.now().toString(), icon, title, body,
    time: new Date().toISOString(), read: false,
  });
}

// Health alerts on new readings — mirrors the app's notification feed.
function evaluateReading(state, r) {
  const bp = getBPStatus(r.systolic, r.diastolic);
  if (bp === 'high') {
    pushNotification(state, 'alert-circle', 'High Blood Pressure',
      `Reading of ${r.systolic}/${r.diastolic} is high. Consider seeing a doctor.`);
  } else if (bp === 'elevated') {
    pushNotification(state, 'alert-circle', 'BP Slightly Elevated',
      `Reading of ${r.systolic}/${r.diastolic} is above normal. Consider rest and hydration.`);
  }
  if (getHRStatus(r.heartRate) === 'abnormal') {
    pushNotification(state, 'heart', 'Heart Rate Abnormal',
      `Resting HR of ${r.heartRate} bpm is outside the 60-100 range.`);
  }
  if (r.spO2 && getSpO2Status(r.spO2) !== 'normal') {
    pushNotification(state, 'pulse', 'Low Blood Oxygen',
      `SpO2 of ${r.spO2}% is below normal. Re-measure and rest.`);
  }
  if (r.steps >= 10000) {
    pushNotification(state, 'footsteps', 'Step Goal Reached!',
      `You hit ${r.steps} steps. Keep up the great work!`);
  }
}

// ── Features ─────────────────────────────────────────────────────────────────
function dashboard(state) {
  const r = state.records[0];
  console.log('\n== Dashboard ==');
  console.log(`User: ${state.user.name}  (${state.user.email})`);
  if (!r) {
    console.log('No readings logged yet. Use "Log health data" to add your first one.');
    return;
  }
  const rows = [
    ['Date',        fmtDate(r.date), ''],
    ['Weight',      r.weight != null ? `${r.weight} kg` : '-', ''],
    ['Blood press.', r.systolic ? `${r.systolic}/${r.diastolic} mmHg` : '-', getBPStatus(r.systolic, r.diastolic) || ''],
    ['Heart rate',  r.heartRate ? `${r.heartRate} bpm` : '-', getHRStatus(r.heartRate) || ''],
    ['Steps',       r.steps != null ? String(r.steps) : '-', ''],
    ['Sleep',       r.sleep != null ? `${r.sleep} h` : '-', r.sleep != null ? getSleepStatus(r.sleep) : ''],
    ['SpO2',        r.spO2 != null ? `${r.spO2} %` : '-', r.spO2 != null ? getSpO2Status(r.spO2) : ''],
    ['Water',       r.water != null ? `${r.water} L` : '-', ''],
  ];
  for (const [k, v, s] of rows) console.log(`  ${k.padEnd(13)} ${String(v).padEnd(16)} ${s}`);
  console.log(`  Overall: ${getOverallStatus(r)}`);
  const unread = state.notifications.filter((n) => !n.read).length;
  if (unread) console.log(`  (${unread} unread notification${unread > 1 ? 's' : ''})`);
}

async function logReading(state, ask) {
  console.log('\n== Log health data (blank = skip a field) ==');
  const num = async (q) => {
    const v = (await ask(q)).trim();
    return v === '' ? undefined : Number(v);
  };
  const entry = {
    id: Date.now().toString(),
    date: new Date().toISOString(),
    weight:    await num('Weight (kg): '),
    systolic:  await num('Systolic BP: '),
    diastolic: await num('Diastolic BP: '),
    heartRate: await num('Heart rate (bpm): '),
    steps:     await num('Steps: '),
    sleep:     await num('Sleep (hours): '),
    spO2:      await num('SpO2 (%): '),
    water:     await num('Water (litres): '),
    notes:     (await ask('Notes: ')).trim(),
  };
  state.records.unshift(entry);
  evaluateReading(state, entry);
  save(state);
  console.log('Saved.');
}

function history(state, n = 14) {
  console.log(`\n== History (last ${n}) ==`);
  if (!state.records.length) return console.log('No readings yet.');
  console.log('  date        weight  BP       HR   steps  sleep  SpO2  water');
  for (const r of state.records.slice(0, n)) {
    console.log(
      `  ${fmtDate(r.date)}  ${String(r.weight ?? '-').padEnd(6)}` +
      `  ${(r.systolic ? `${r.systolic}/${r.diastolic}` : '-').padEnd(7)}` +
      `  ${String(r.heartRate ?? '-').padEnd(3)}  ${String(r.steps ?? '-').padEnd(5)}` +
      `  ${String(r.sleep ?? '-').padEnd(5)}  ${String(r.spO2 ?? '-').padEnd(4)}  ${r.water ?? '-'}`
    );
    if (r.notes) console.log(`              note: ${r.notes}`);
  }
}

function trends(state) {
  console.log('\n== Trends (oldest -> newest, last 30) ==');
  if (!state.records.length) return console.log('No readings yet.');
  const recent = state.records.slice(0, 30).reverse();
  const metric = (label, key, unit) => {
    const vals = recent.map((r) => r[key]).filter((v) => v != null);
    if (!vals.length) return;
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    console.log(`  ${label.padEnd(11)} ${sparkline(recent.map((r) => r[key]))}` +
      `  min ${Math.min(...vals)}  avg ${avg.toFixed(1)}  max ${Math.max(...vals)} ${unit}`);
  };
  metric('Weight',    'weight',    'kg');
  metric('Systolic',  'systolic',  'mmHg');
  metric('Diastolic', 'diastolic', 'mmHg');
  metric('Heart rate', 'heartRate', 'bpm');
  metric('Steps',     'steps',     '');
  metric('Sleep',     'sleep',     'h');
  metric('SpO2',      'spO2',      '%');
  metric('Water',     'water',     'L');
}

function listGoals(state) {
  console.log('\n== Goals ==');
  if (!state.goals.length) return console.log('No goals yet.');
  for (const g of state.goals) {
    const target = g.type === 'bp' ? `${g.targetSys}/${g.targetDia}` : `${g.target} ${g.unit || ''}`;
    console.log(`  [${g.achieved ? 'x' : ' '}] ${g.title}  (target ${target}, by ${g.deadline || 'n/a'}) — ${g.status}`);
  }
}

async function addGoal(state, ask) {
  console.log('\n== New goal ==');
  const goal = {
    id: Date.now().toString(),
    type:  (await ask('Type (weight/bp/steps/sleep/water): ')).trim() || 'weight',
    title: (await ask('Title: ')).trim(),
    deadline: (await ask('Deadline (YYYY-MM-DD): ')).trim(),
    status: 'on_track', achieved: false,
  };
  if (goal.type === 'bp') {
    goal.targetSys = Number(await ask('Target systolic: '));
    goal.targetDia = Number(await ask('Target diastolic: '));
  } else {
    goal.target = Number(await ask('Target value: '));
    goal.unit = (await ask('Unit (kg/steps/h/L): ')).trim();
  }
  state.goals.unshift(goal);
  save(state);
  console.log('Goal added.');
}

function listReminders(state) {
  console.log('\n== Reminders ==');
  state.reminders.forEach((r, i) =>
    console.log(`  ${i + 1}. [${r.enabled ? 'on ' : 'off'}] ${r.label} — ${r.time}`));
}

async function toggleReminder(state, ask) {
  listReminders(state);
  const idx = Number(await ask('Toggle which number? ')) - 1;
  if (!state.reminders[idx]) return console.log('Invalid number.');
  state.reminders[idx].enabled = !state.reminders[idx].enabled;
  save(state);
  console.log(`${state.reminders[idx].label} is now ${state.reminders[idx].enabled ? 'on' : 'off'}.`);
}

async function addReminder(state, ask) {
  const label = (await ask('Label: ')).trim();
  const time = (await ask('Time (e.g. 7:00 AM): ')).trim();
  state.reminders.push({ id: Date.now().toString(), label, time, enabled: true });
  save(state);
  console.log('Reminder added.');
}

function notifications(state) {
  console.log('\n== Notifications ==');
  if (!state.notifications.length) return console.log('No notifications.');
  for (const n of state.notifications.slice(0, 15)) {
    console.log(`  ${n.read ? ' ' : '*'} ${n.title} — ${n.body}`);
  }
  state.notifications.forEach((n) => { n.read = true; });
  save(state);
}

function profile(state) {
  console.log('\n== Profile ==');
  const u = state.user;
  console.log(`  Name:   ${u.name}\n  Email:  ${u.email}\n  Age:    ${u.age}\n  Height: ${u.height}`);
  console.log(`  Readings logged: ${state.records.length}`);
}

async function editProfile(state, ask) {
  const u = state.user;
  u.name  = (await ask(`Name [${u.name}]: `)).trim() || u.name;
  u.email = (await ask(`Email [${u.email}]: `)).trim() || u.email;
  const age = (await ask(`Age [${u.age}]: `)).trim();
  if (age) u.age = Number(age);
  u.height = (await ask(`Height [${u.height}]: `)).trim() || u.height;
  save(state);
  console.log('Profile updated.');
}

// ── Main loop ────────────────────────────────────────────────────────────────
async function main() {
  const state = load();

  if (process.argv[2] === 'dashboard') {
    dashboard(state);
    return;
  }

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  // Buffer incoming lines so piped/pasted input isn't dropped between
  // questions (rl.question alone loses lines that arrive while no
  // question is pending).
  const lines = [];
  const waiters = [];
  let closed = false;
  rl.on('line', (l) => {
    const w = waiters.shift();
    if (w) w(l); else lines.push(l);
  });
  rl.on('close', () => {
    closed = true;
    while (waiters.length) waiters.shift()('0');
  });
  const ask = (q) => {
    process.stdout.write(q);
    if (lines.length) return Promise.resolve(lines.shift());
    if (closed) return Promise.resolve('0');
    return new Promise((res) => waiters.push(res));
  };

  console.log('==========================================');
  console.log('  Personal Health Monitor — terminal');
  console.log('==========================================');

  const actions = [
    ['Dashboard',            () => dashboard(state)],
    ['Log health data',      () => logReading(state, ask)],
    ['History',              () => history(state)],
    ['Trends',               () => trends(state)],
    ['Goals',                () => listGoals(state)],
    ['Add goal',             () => addGoal(state, ask)],
    ['Reminders',            () => listReminders(state)],
    ['Toggle reminder',      () => toggleReminder(state, ask)],
    ['Add reminder',         () => addReminder(state, ask)],
    ['Notifications',        () => notifications(state)],
    ['Profile',              () => profile(state)],
    ['Edit profile',         () => editProfile(state, ask)],
  ];

  for (;;) {
    console.log('\n===== Menu =====');
    actions.forEach(([label], i) => console.log(`  ${i + 1}. ${label}`));
    console.log('  0. Exit');
    const choice = (await ask('> ')).trim();
    if (choice === '0') break;
    const entry = actions[Number(choice) - 1];
    if (!entry) { console.log('Invalid choice.'); continue; }
    try {
      await entry[1]();
    } catch (e) {
      console.log(`Error: ${e.message}`);
    }
  }
  rl.close();
  console.log('Bye.');
}

main();
