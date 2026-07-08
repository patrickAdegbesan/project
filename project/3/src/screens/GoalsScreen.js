import React, { useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Modal, TextInput, Platform, StatusBar,
} from 'react-native';
import { Colors, Typography, S, R, Shadow } from '../theme';
import { useHealth } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import CircularProgress from '../components/CircularProgress';
import StatusBadge from '../components/StatusBadge';
import Card from '../components/Card';
import Icon from '../components/Icon';

const GOAL_TYPES = [
  { key: 'weight', label: 'Weight',         icon: 'scale-outline' },
  { key: 'bp',     label: 'Blood Pressure', icon: 'heart-outline' },
  { key: 'hr',     label: 'Heart Rate',     icon: 'pulse-outline' },
  { key: 'steps',  label: 'Steps',          icon: 'footsteps' },
  { key: 'sleep',  label: 'Sleep',          icon: 'moon-outline' },
];

const STATUS_COLOR = {
  on_track: Colors.accent,
  watch:    Colors.warning,
  alert:    Colors.danger,
};

function GoalCard({ goal }) {
  const { colors: c } = useTheme();
  const isWeight = goal.type === 'weight';
  const isBP     = goal.type === 'bp';

  let percent = 0;
  if (isWeight) {
    const start = 75, target = goal.target, current = goal.current;
    percent = Math.min(100, Math.max(0, ((start - current) / (start - target)) * 100));
  } else if (isBP) {
    const sP = Math.min(100, Math.max(0, ((140 - goal.currentSys) / (140 - goal.targetSys)) * 100));
    const dP = Math.min(100, Math.max(0, ((90 - goal.currentDia) / (90 - goal.targetDia)) * 100));
    percent = (sP + dP) / 2;
  } else {
    percent = 65;
  }

  const color = STATUS_COLOR[goal.status] || Colors.accent;
  const icon  = GOAL_TYPES.find(t => t.key === goal.type)?.icon || 'trophy-outline';
  const days  = Math.max(0, Math.round((new Date(goal.deadline) - new Date()) / 86400000));

  return (
    <Card style={[s.goalCard, goal.achieved && { opacity: 0.55 }]}>
      {goal.achieved && (
        <View style={[s.achievedBadge, { backgroundColor: c.success_bg }]}>
          <Icon name="ribbon" size={14} color={Colors.accent} />
          <Text style={s.achievedText}>Achieved!</Text>
        </View>
      )}
      <View style={s.goalTop}>
        <View style={s.goalLeft}>
          <View style={[s.goalIconWrap, { backgroundColor: color + '14' }]}>
            <Icon name={icon} size={20} color={color} />
          </View>
          <Text style={[s.goalTitle, { color: c.text1 }]}>{goal.title}</Text>
          {isBP ? (
            <Text style={[s.goalDetail, { color: c.text2 }]}>
              Current: {goal.currentSys}/{goal.currentDia} → Target: {goal.targetSys}/{goal.targetDia}
            </Text>
          ) : isWeight ? (
            <Text style={[s.goalDetail, { color: c.text2 }]}>
              Current: {goal.current} kg → Target: {goal.target} kg
            </Text>
          ) : null}
        </View>
        <View style={s.goalRight}>
          <CircularProgress percent={percent} size={62} color={color} />
          <Text style={[s.goalPercent, { color }]}>{Math.round(percent)}%</Text>
        </View>
      </View>

      {isBP && (
        <View style={[s.progressBarWrap, { backgroundColor: c.border }]}>
          <View style={[s.progressBg, { backgroundColor: c.border }]}>
            <View style={[s.progressFill, { width: `${Math.min(100, percent)}%`, backgroundColor: color }]} />
          </View>
        </View>
      )}

      <View style={s.goalFooter}>
        <View style={s.deadlineWrap}>
          <Icon name="calendar-outline" size={13} color={c.text3} />
          <Text style={[s.deadlineText, { color: c.text3 }]}>
            {days > 0 ? `${days} days left` : 'Due today'}  ·  {new Date(goal.deadline).toLocaleDateString('en-US',{month:'short',day:'numeric'})}
          </Text>
        </View>
        <StatusBadge status={goal.status} />
      </View>
    </Card>
  );
}

export default function GoalsScreen() {
  const { colors: c, isDark } = useTheme();
  const { goals, addGoal, streak, records } = useHealth();
  const [modal, setModal] = useState(false);
  const [goalType, setGoalType] = useState('weight');
  const [target, setTarget]     = useState('');
  const [deadline, setDeadline] = useState('2026-08-01');

  const handleAdd = () => {
    if (!target) return;
    const typeInfo = GOAL_TYPES.find(t => t.key === goalType);
    addGoal({
      type: goalType, title: `${typeInfo.label} Goal`,
      target: parseFloat(target), current: goalType === 'weight' ? 72.5 : 0,
      unit: goalType === 'weight' ? 'kg' : 'bpm', deadline,
    });
    setModal(false); setTarget('');
  };

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      <View style={s.header}>
        <Text style={s.headerTitle}>Health Goals</Text>
        <TouchableOpacity style={s.addBtn} onPress={() => setModal(true)}>
          <Icon name="add" size={18} color={Colors.white} />
          <Text style={s.addBtnText}>New Goal</Text>
        </TouchableOpacity>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={s.scroll}>

        {/* Streak Banner */}
        <View style={[s.streakBanner, { backgroundColor: c.card, borderColor: Colors.warning + '30' }]}>
          <View style={s.streakLeft}>
            <Icon name="flame" size={28} color={Colors.warning} />
            <View>
              <Text style={[s.streakNum, { color: c.text1 }]}>{streak}-Day Streak</Text>
              <Text style={[s.streakSub, { color: c.text2 }]}>Keep logging to maintain your streak!</Text>
            </View>
          </View>
          <View style={s.streakBadge}>
            <Icon name="trophy" size={13} color={Colors.warning} />
            <Text style={s.streakBadgeText}> Best</Text>
          </View>
        </View>

        {/* Goals */}
        {goals.length > 0 ? (
          <>
            <Text style={[s.sectionTitle, { color: c.text1 }]}>Active Goals</Text>
            {goals.map(g => <GoalCard key={g.id} goal={g} />)}
          </>
        ) : (
          <Card style={s.emptyCard}>
            <Icon name="trophy-outline" size={48} color={c.text3} style={{ alignSelf: 'center', marginBottom: 12 }} />
            <Text style={[s.emptyTitle, { color: c.text1 }]}>No goals yet</Text>
            <Text style={[s.emptySub, { color: c.text2 }]}>Set your first health target and start tracking your progress.</Text>
            <TouchableOpacity style={s.emptyBtn} onPress={() => setModal(true)}>
              <Icon name="add" size={16} color={Colors.white} />
              <Text style={s.emptyBtnText}>Create a Goal</Text>
            </TouchableOpacity>
          </Card>
        )}

        <View style={{ height: 110 }} />
      </ScrollView>

      {/* Add Goal Modal */}
      <Modal visible={modal} transparent animationType="slide">
        <TouchableOpacity style={[s.overlay, { backgroundColor: c.overlay }]} activeOpacity={1} onPress={() => setModal(false)} />
        <View style={[s.sheet, { backgroundColor: c.card }]}>
          <View style={[s.sheetHandle, { backgroundColor: c.border }]} />
          <Text style={[s.sheetTitle, { color: c.text1 }]}>New Health Goal</Text>
          <Text style={[s.sheetSub, { color: c.text2 }]}>Choose a metric and set your target</Text>

          <Text style={[s.fieldLabel, { color: c.text2 }]}>Goal Type</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={[s.typeRow, { flexWrap: 'nowrap' }]}>
            {GOAL_TYPES.map(t => (
              <TouchableOpacity
                key={t.key}
                onPress={() => setGoalType(t.key)}
                style={[s.typeBtn, { borderColor: c.border, backgroundColor: c.input_bg }, goalType === t.key && s.typeBtnActive]}
              >
                <Icon name={t.icon} size={16} color={goalType === t.key ? Colors.white : c.text2} />
                <Text style={[s.typeBtnText, { color: c.text2 }, goalType === t.key && s.typeBtnTextActive]}>{t.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
          </ScrollView>

          <Text style={[s.fieldLabel, { color: c.text2 }]}>Target Value</Text>
          <View style={[s.sheetInputWrap, { backgroundColor: c.input_bg, borderColor: c.border }]}>
            <TextInput
              style={[s.sheetInput, { color: c.text1 }]}
              placeholder={goalType === 'weight' ? '70  kg' : goalType === 'bp' ? '120  mmHg' : '65  bpm'}
              placeholderTextColor={c.text3}
              value={target}
              onChangeText={setTarget}
              keyboardType="decimal-pad"
            />
          </View>

          <Text style={[s.fieldLabel, { color: c.text2 }]}>Deadline</Text>
          <View style={[s.sheetInputWrap, { backgroundColor: c.input_bg, borderColor: c.border }]}>
            <Icon name="calendar-outline" size={16} color={c.text3} style={{ marginRight: 10 }} />
            <TextInput
              style={[s.sheetInput, { flex: 1, color: c.text1 }]}
              value={deadline}
              onChangeText={setDeadline}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={c.text3}
            />
          </View>

          <View style={s.sheetBtns}>
            <TouchableOpacity style={[s.sheetCancel, { borderColor: c.border }]} onPress={() => setModal(false)}>
              <Text style={[s.sheetCancelText, { color: c.text2 }]}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.sheetSave} onPress={handleAdd}>
              <Icon name="checkmark" size={16} color={Colors.white} />
              <Text style={s.sheetSaveText}>Set Goal</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const s = StyleSheet.create({
  root:   { flex: 1 },
  header: {
    backgroundColor: Colors.primary,
    paddingTop: 52, paddingBottom: 16, paddingHorizontal: S.xl,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  headerTitle: { ...Typography.h2, color: Colors.white },
  addBtn:      { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: Colors.accent, borderRadius: R.md, paddingHorizontal: 14, paddingVertical: 9 },
  addBtnText:  { ...Typography.bodySm, color: Colors.white, fontWeight: '700' },

  scroll:      { padding: S.xl, gap: 14 },
  sectionTitle:{ ...Typography.h4 },

  streakBanner: {
    borderRadius: R.xl, padding: S.lg, flexDirection: 'row', alignItems: 'center',
    justifyContent: 'space-between', borderWidth: 1, ...Shadow.sm,
  },
  streakLeft:   { flexDirection: 'row', alignItems: 'center', gap: 12 },
  streakNum:    { ...Typography.h4 },
  streakSub:    { ...Typography.bodySm, marginTop: 1 },
  streakBadge:  { backgroundColor: Colors.warning + '14', borderRadius: R.full, paddingHorizontal: 12, paddingVertical: 5 },
  streakBadgeText:{ ...Typography.bodySm, color: Colors.warning, fontWeight: '700' },

  goalCard:   { gap: 12 },
  achievedBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, alignSelf: 'flex-start', borderRadius: R.full, paddingHorizontal: 10, paddingVertical: 4 },
  achievedText:  { ...Typography.label, color: Colors.accent, textTransform: 'none', fontWeight: '700', letterSpacing: 0 },

  goalTop:   { flexDirection: 'row', alignItems: 'flex-start' },
  goalLeft:  { flex: 1, gap: 6 },
  goalIconWrap: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 4 },
  goalTitle: { ...Typography.h4 },
  goalDetail:{ ...Typography.bodySm },
  goalRight: { alignItems: 'center', gap: 4 },
  goalPercent:{ ...Typography.label, fontWeight: '700', textTransform: 'none', letterSpacing: 0 },

  progressBarWrap: { height: 6, borderRadius: 3, overflow: 'hidden' },
  progressBg:      { flex: 1, borderRadius: 3 },
  progressFill:    { height: 6, borderRadius: 3 },

  goalFooter: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  deadlineWrap:{ flexDirection: 'row', alignItems: 'center', gap: 5 },
  deadlineText:{ ...Typography.bodySm },

  emptyCard: { alignItems: 'center', padding: S.xxl },
  emptyTitle:{ ...Typography.h3, marginBottom: 6 },
  emptySub:  { ...Typography.bodySm, textAlign: 'center', marginBottom: 20 },
  emptyBtn:  { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: Colors.primary, borderRadius: R.md, paddingHorizontal: 20, paddingVertical: 12 },
  emptyBtnText:{ ...Typography.bodySm, color: Colors.white, fontWeight: '700' },

  overlay: { flex: 1 },
  sheet: {
    borderTopLeftRadius: R.xxl, borderTopRightRadius: R.xxl,
    padding: S.xl, paddingBottom: Platform.OS === 'ios' ? 36 : S.xl,
    gap: 12,
  },
  sheetHandle: { width: 36, height: 4, borderRadius: 2, alignSelf: 'center', marginBottom: 4 },
  sheetTitle:  { ...Typography.h3 },
  sheetSub:    { ...Typography.bodySm, marginTop: -4 },
  fieldLabel:  { ...Typography.label, textTransform: 'uppercase' },

  typeRow: { flexDirection: 'row', gap: 8 },
  typeBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 5,
    paddingVertical: 10, borderRadius: R.md, borderWidth: 1.5,
  },
  typeBtnActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  typeBtnText:   { ...Typography.label, textTransform: 'none', fontWeight: '600', letterSpacing: 0 },
  typeBtnTextActive: { color: Colors.white },

  sheetInputWrap: {
    flexDirection: 'row', alignItems: 'center',
    borderRadius: R.md, borderWidth: 1.5, paddingHorizontal: 14, height: 52,
  },
  sheetInput: { flex: 1, ...Typography.body, padding: 0 },

  sheetBtns: { flexDirection: 'row', gap: 10, marginTop: 4 },
  sheetCancel: { flex: 1, alignItems: 'center', paddingVertical: 14, borderRadius: R.md, borderWidth: 1.5 },
  sheetCancelText: { ...Typography.bodySm, fontWeight: '600' },
  sheetSave: { flex: 2, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, backgroundColor: Colors.primary, borderRadius: R.md, paddingVertical: 14 },
  sheetSaveText: { ...Typography.bodySm, color: Colors.white, fontWeight: '700' },
});
