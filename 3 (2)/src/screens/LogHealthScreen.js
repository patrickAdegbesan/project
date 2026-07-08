import React, { useState, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ScrollView, KeyboardAvoidingView, Platform, Animated, StatusBar,
} from 'react-native';
import { Colors, Typography, S, R, Shadow } from '../theme';
import { useHealth, getBPStatus, getHRStatus } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import Icon from '../components/Icon';
import Card from '../components/Card';

const BP_CFG = {
  normal:   { border: Colors.accent,   bg: Colors.success_bg, icon: 'checkmark-circle', color: Colors.accent,  msg: 'Normal range — great job!' },
  elevated: { border: Colors.warning,  bg: Colors.warning_bg, icon: 'warning',          color: Colors.warning, msg: 'Elevated — keep monitoring.' },
  high:     { border: Colors.danger,   bg: Colors.danger_bg,  icon: 'alert-circle',     color: Colors.danger,  msg: 'High — consider seeing a doctor.' },
};
const HR_CFG = {
  normal:   { border: Colors.accent,  bg: Colors.success_bg, icon: 'checkmark-circle', color: Colors.accent, msg: 'Normal resting heart rate.' },
  abnormal: { border: Colors.danger,  bg: Colors.danger_bg,  icon: 'alert-circle',     color: Colors.danger, msg: 'Outside normal range (60–100 bpm).' },
};

function FieldCard({ iconName, title, children, status, statusMsg, statusIcon, statusColor, statusBg, statusBorder }) {
  const { colors: c } = useTheme();
  return (
    <View style={[s.fieldCard, { backgroundColor: c.card, borderColor: status ? statusBorder : c.border_light }, status && { borderWidth: 1.5 }]}>
      <View style={s.fieldHeader}>
        <View style={[s.fieldIconWrap, { backgroundColor: Colors.primary + '12' }]}>
          <Icon name={iconName} size={18} color={Colors.primary} />
        </View>
        <Text style={[s.fieldTitle, { color: c.text1 }]}>{title}</Text>
      </View>
      {children}
      {status && (
        <View style={[s.feedback, { backgroundColor: statusBg }]}>
          <Icon name={statusIcon} size={15} color={statusColor} />
          <Text style={[s.feedbackText, { color: statusColor }]}>{statusMsg}</Text>
        </View>
      )}
    </View>
  );
}

function NumInput({ value, onChangeText, placeholder, unit, wide }) {
  const { colors: c } = useTheme();
  const [focused, setFocused] = useState(false);
  return (
    <View style={[
      s.numWrap, wide && s.numWrapWide,
      { backgroundColor: focused ? c.card : c.input_bg, borderColor: focused ? Colors.primary : c.border },
    ]}>
      <TextInput
        style={[s.numInput, { color: c.text1 }]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={c.text3}
        keyboardType="decimal-pad"
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
      />
      <Text style={[s.numUnit, { color: c.text3 }]}>{unit}</Text>
    </View>
  );
}

export default function LogHealthScreen({ navigation }) {
  const { colors: c } = useTheme();
  const { addRecord } = useHealth();
  const [weight, setWeight]       = useState('');
  const [unit, setUnit]           = useState('kg');
  const [systolic, setSystolic]   = useState('');
  const [diastolic, setDiastolic] = useState('');
  const [heartRate, setHeartRate] = useState('');
  const [steps, setSteps]         = useState('');
  const [sleep, setSleep]         = useState('');
  const [spO2, setSpO2]           = useState('');
  const [water, setWater]         = useState('');
  const [notes, setNotes]         = useState('');
  const [saved, setSaved]         = useState(false);
  const slideAnim = useRef(new Animated.Value(80)).current;
  const opAnim    = useRef(new Animated.Value(0)).current;

  const bpStatus = getBPStatus(systolic, diastolic);
  const hrStatus = getHRStatus(heartRate);
  const bpCfg    = bpStatus ? BP_CFG[bpStatus] : null;
  const hrCfg    = heartRate ? HR_CFG[hrStatus] : null;

  const now     = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday:'short', month:'short', day:'numeric' });
  const timeStr = now.toLocaleTimeString('en-US', { hour:'numeric', minute:'2-digit' });

  const handleSave = () => {
    if (!weight && !systolic && !heartRate && !steps) return;
    const toFloat = (v) => { const n = parseFloat(v); return isNaN(n) || n === 0 ? null : n; };
    const toInt   = (v) => { const n = parseInt(v, 10); return isNaN(n) || n === 0 ? null : n; };
    addRecord({
      weight:    toFloat(weight),
      systolic:  toInt(systolic),
      diastolic: toInt(diastolic),
      heartRate: toInt(heartRate),
      steps:     toInt(steps),
      sleep:     toFloat(sleep),
      spO2:      toFloat(spO2),
      water:     toFloat(water),
      notes,
    });
    setSaved(true);
    Animated.parallel([
      Animated.spring(slideAnim, { toValue: 0, useNativeDriver: true }),
      Animated.timing(opAnim,    { toValue: 1, duration: 250, useNativeDriver: true }),
    ]).start();
    setTimeout(() => {
      Animated.parallel([
        Animated.timing(slideAnim, { toValue: 80, duration: 300, useNativeDriver: true }),
        Animated.timing(opAnim,    { toValue: 0,  duration: 300, useNativeDriver: true }),
      ]).start(() => {
        setSaved(false);
        navigation.navigate('Home');
      });
    }, 1600);
  };

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      <View style={s.header}>
        <TouchableOpacity onPress={() => navigation.navigate('Home')} style={s.backBtn}>
          <Icon name="arrow-back" size={22} color={Colors.white} />
        </TouchableOpacity>
        <View style={s.headerCenter}>
          <Text style={s.headerTitle}>Log Health Data</Text>
          <Text style={s.headerSub}>{dateStr} · {timeStr}</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView
        style={s.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        <ScrollView
          contentContainerStyle={s.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Weight */}
          <FieldCard iconName="scale-outline" title="Weight">
            <View style={s.unitRow}>
              {['kg', 'lbs'].map(u => (
                <TouchableOpacity
                  key={u} onPress={() => setUnit(u)}
                  style={[s.unitBtn, { borderColor: c.border, backgroundColor: c.input_bg }, unit === u && s.unitBtnActive]}
                >
                  <Text style={[s.unitBtnText, { color: c.text2 }, unit === u && s.unitBtnTextActive]}>{u}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <NumInput value={weight} onChangeText={setWeight} placeholder="72.5" unit={unit} wide />
          </FieldCard>

          {/* Blood Pressure */}
          <FieldCard
            iconName="heart-outline"
            title="Blood Pressure"
            status={bpCfg}
            statusMsg={bpCfg?.msg}
            statusIcon={bpCfg?.icon}
            statusColor={bpCfg?.color}
            statusBg={bpCfg?.bg}
            statusBorder={bpCfg?.border}
          >
            <View style={s.bpRow}>
              <View style={s.bpHalf}>
                <Text style={[s.bpLabel, { color: c.text3 }]}>Systolic</Text>
                <NumInput value={systolic} onChangeText={setSystolic} placeholder="120" unit="mmHg" />
              </View>
              <View style={s.bpSlash}><Text style={[s.slashText, { color: c.border }]}>/</Text></View>
              <View style={s.bpHalf}>
                <Text style={[s.bpLabel, { color: c.text3 }]}>Diastolic</Text>
                <NumInput value={diastolic} onChangeText={setDiastolic} placeholder="80" unit="mmHg" />
              </View>
            </View>
          </FieldCard>

          {/* Heart Rate */}
          <FieldCard
            iconName="pulse-outline"
            title="Heart Rate"
            status={hrCfg}
            statusMsg={hrCfg?.msg}
            statusIcon={hrCfg?.icon}
            statusColor={hrCfg?.color}
            statusBg={hrCfg?.bg}
            statusBorder={hrCfg?.border}
          >
            <NumInput value={heartRate} onChangeText={setHeartRate} placeholder="72" unit="bpm" wide />
          </FieldCard>

          {/* Activity */}
          <FieldCard iconName="footsteps" title="Daily Steps">
            <NumInput value={steps} onChangeText={setSteps} placeholder="8000" unit="steps" wide />
          </FieldCard>

          {/* Sleep */}
          <FieldCard iconName="moon-outline" title="Sleep Duration">
            <NumInput value={sleep} onChangeText={setSleep} placeholder="7.5" unit="hrs" wide />
          </FieldCard>

          {/* SpO2 & Water */}
          <FieldCard iconName="heart-circle-outline" title="Blood Oxygen & Water">
            <View style={s.bpRow}>
              <View style={s.bpHalf}>
                <Text style={[s.bpLabel, { color: c.text3 }]}>SpO₂</Text>
                <NumInput value={spO2} onChangeText={setSpO2} placeholder="98" unit="%" />
              </View>
              <View style={s.bpSlash} />
              <View style={s.bpHalf}>
                <Text style={[s.bpLabel, { color: c.text3 }]}>Water</Text>
                <NumInput value={water} onChangeText={setWater} placeholder="2.0" unit="L" />
              </View>
            </View>
          </FieldCard>

          {/* Notes */}
          <FieldCard iconName="document-text-outline" title="Notes (optional)">
            <TextInput
              style={[s.notesInput, { backgroundColor: c.input_bg, borderColor: c.border, color: c.text1 }]}
              placeholder="How are you feeling today?"
              placeholderTextColor={c.text3}
              value={notes}
              onChangeText={setNotes}
              multiline
              numberOfLines={3}
              textAlignVertical="top"
            />
          </FieldCard>

          <View style={{ height: 100 }} />
        </ScrollView>

        {/* Footer */}
        <View style={[s.footer, { backgroundColor: c.card, borderTopColor: c.border_light }]}>
          <TouchableOpacity style={s.cancelBtn} onPress={() => navigation.navigate('Home')}>
            <Text style={[s.cancelText, { color: c.text2 }]}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.saveBtn} onPress={handleSave} activeOpacity={0.86}>
            <Icon name="checkmark" size={18} color={Colors.white} />
            <Text style={s.saveBtnText}>Save Record</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      {/* Success toast */}
      {saved && (
        <Animated.View style={[s.toast, { opacity: opAnim, transform: [{ translateY: slideAnim }] }]}>
          <View style={s.toastInner}>
            <Icon name="checkmark-circle" size={22} color={Colors.white} />
            <Text style={s.toastText}>Health data saved successfully!</Text>
          </View>
        </Animated.View>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.bg },
  flex: { flex: 1 },
  header: {
    backgroundColor: Colors.primary,
    paddingTop: 52, paddingBottom: 16, paddingHorizontal: S.xl,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  backBtn:      { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center' },
  headerCenter: { alignItems: 'center' },
  headerTitle:  { ...Typography.h4, color: Colors.white },
  headerSub:    { ...Typography.label, color: 'rgba(255,255,255,0.55)', textTransform: 'none', fontWeight: '400', letterSpacing: 0, marginTop: 2 },

  scroll: { padding: S.xl, gap: 14 },

  fieldCard: {
    backgroundColor: Colors.card, borderRadius: R.xl,
    padding: S.lg, ...Shadow.sm,
    borderWidth: 1, borderColor: Colors.border_light, gap: 14,
  },
  fieldHeader:  { flexDirection: 'row', alignItems: 'center', gap: 10 },
  fieldIconWrap:{ width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  fieldTitle:   { ...Typography.h4, color: Colors.text1 },

  unitRow: { flexDirection: 'row', gap: 8 },
  unitBtn: { paddingHorizontal: 18, paddingVertical: 7, borderRadius: R.full, borderWidth: 1.5, borderColor: Colors.border, backgroundColor: Colors.input_bg },
  unitBtnActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  unitBtnText:   { ...Typography.bodySm, color: Colors.text2, fontWeight: '600' },
  unitBtnTextActive: { color: Colors.white },

  numWrap: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: Colors.input_bg, borderRadius: R.md,
    borderWidth: 1.5, borderColor: Colors.border,
    paddingHorizontal: 14, paddingVertical: 12,
  },
  numWrapWide:    { flex: 1 },
  numWrapFocused: { borderColor: Colors.primary, backgroundColor: Colors.white },
  numInput: { flex: 1, ...Typography.mono, color: Colors.text1, padding: 0, fontSize: 26 },
  numUnit:  { ...Typography.bodySm, color: Colors.text3, fontWeight: '600', marginLeft: 8 },

  bpRow:   { flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  bpHalf:  { flex: 1, gap: 6 },
  bpLabel: { ...Typography.label, color: Colors.text3, textTransform: 'uppercase' },
  bpSlash: { paddingBottom: 12 },
  slashText:{ ...Typography.h2, color: Colors.border },

  feedback: { flexDirection: 'row', alignItems: 'center', gap: 8, borderRadius: R.md, padding: 12 },
  feedbackText: { ...Typography.bodySm, fontWeight: '600', flex: 1 },

  notesInput: {
    backgroundColor: Colors.input_bg, borderRadius: R.md,
    borderWidth: 1.5, borderColor: Colors.border,
    padding: 14, ...Typography.body, color: Colors.text1, minHeight: 90,
  },

  footer: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    paddingHorizontal: S.xl, paddingVertical: 14,
    paddingBottom: Platform.OS === 'ios' ? 30 : 14,
    backgroundColor: Colors.card,
    borderTopWidth: 1, borderTopColor: Colors.border_light,
    ...Shadow.sm,
  },
  cancelBtn:    { paddingHorizontal: 16, paddingVertical: 14 },
  cancelText:   { ...Typography.bodySm, color: Colors.text2, fontWeight: '600' },
  saveBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    backgroundColor: Colors.primary, borderRadius: R.md, height: 52, ...Shadow.md,
  },
  saveBtnText: { ...Typography.h4, color: Colors.white },

  toast: { position: 'absolute', bottom: 90, left: S.xl, right: S.xl },
  toastInner: {
    backgroundColor: Colors.accent, borderRadius: R.lg,
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 16, ...Shadow.lg,
  },
  toastText: { ...Typography.bodySm, color: Colors.white, fontWeight: '700', flex: 1 },
});
