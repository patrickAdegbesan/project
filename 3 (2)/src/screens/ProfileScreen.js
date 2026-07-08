import React, { useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Switch, Modal, StatusBar,
} from 'react-native';
import { Colors, Typography, S, R, Shadow } from '../theme';
import { useHealth } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import Icon from '../components/Icon';
import Card from '../components/Card';

// ── Reusable sub-components ──────────────────────────────────────────────────

function SettingRow({ iconName, iconColor, label, sub, right, onPress, danger, last }) {
  const { colors: c, isDark } = useTheme();
  const ic = danger ? Colors.danger : (iconColor || Colors.primary);
  const iconBg = ic + (isDark ? '30' : '18');

  return (
    <TouchableOpacity
      style={[
        s.settingRow,
        !last && { borderBottomWidth: 1, borderBottomColor: c.border_light },
      ]}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
      disabled={!onPress && !right}
    >
      <View style={[s.settingIconWrap, { backgroundColor: iconBg }]}>
        <Icon name={iconName} size={17} color={ic} />
      </View>
      <View style={s.settingCenter}>
        <Text style={[s.settingLabel, { color: danger ? Colors.danger : c.text1 }]}>{label}</Text>
        {sub ? <Text style={[s.settingSub, { color: c.text3 }]}>{sub}</Text> : null}
      </View>
      {right ?? (onPress ? <Icon name="chevron-forward" size={17} color={c.text3} /> : null)}
    </TouchableOpacity>
  );
}

function SectionCard({ title, children }) {
  const { colors: c } = useTheme();
  return (
    <View style={s.section}>
      <Text style={[s.sectionLabel, { color: c.text3 }]}>{title}</Text>
      <Card pad={false}>{children}</Card>
    </View>
  );
}

function SegControl({ options, value, onChange }) {
  const { colors: c } = useTheme();
  return (
    <View style={[s.seg, { borderColor: c.border, backgroundColor: c.border_light }]}>
      {options.map(opt => {
        const active = opt === value;
        return (
          <TouchableOpacity
            key={opt}
            onPress={() => onChange(opt)}
            style={[s.segBtn, active && { backgroundColor: Colors.primary }]}
          >
            <Text style={[s.segTxt, { color: active ? '#fff' : c.text2 }, active && s.segTxtActive]}>
              {opt}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

// ── Screen ────────────────────────────────────────────────────────────────────
export default function ProfileScreen({ navigation }) {
  const { colors: c, isDark, toggleDark } = useTheme();
  const { user, records, goals, streak, reminders, toggleReminder, addReminder } = useHealth();
  const [weightUnit, setWeightUnit]   = useState('kg');
  const [timeFormat, setTimeFormat]   = useState('12hr');
  const [timeout_, setTimeout_]       = useState('15m');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleLogout = () => navigation.getParent()?.replace('Login');

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      {/* Header */}
      <View style={s.header}>
        <Text style={s.headerTitle}>Profile</Text>
        <TouchableOpacity style={s.editBtn}>
          <Icon name="create-outline" size={16} color={Colors.white} />
          <Text style={s.editBtnText}>Edit</Text>
        </TouchableOpacity>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={s.scroll}>

        {/* Profile card */}
        <Card style={s.profileCard}>
          <View style={s.avatarWrap}>
            <View style={[s.avatar, { borderColor: c.border_light }]}>
              <Text style={s.avatarLetter}>{user.name.charAt(0)}</Text>
            </View>
            <TouchableOpacity style={[s.cameraBtn, { borderColor: c.card }]}>
              <Icon name="camera" size={13} color="#fff" />
            </TouchableOpacity>
          </View>
          <Text style={[s.userName, { color: c.text1 }]}>{user.name}</Text>
          <Text style={[s.userEmail, { color: c.text2 }]}>{user.email}</Text>
          <View style={[s.divider, { backgroundColor: c.border_light }]} />
          <View style={s.statsRow}>
            {[
              { label: 'Records', value: `${records.length}` },
              { label: 'Goals',   value: `${goals.length}` },
              { label: 'Streak',  value: `${streak}d` },
            ].map((st, i, arr) => (
              <React.Fragment key={st.label}>
                <View style={s.statItem}>
                  <Text style={[s.statVal, { color: c.text1 }]}>{st.value}</Text>
                  <Text style={[s.statLbl, { color: c.text3 }]}>{st.label}</Text>
                </View>
                {i < arr.length - 1 && <View style={[s.statDivider, { backgroundColor: c.border }]} />}
              </React.Fragment>
            ))}
          </View>
        </Card>

        {/* Account */}
        <SectionCard title="ACCOUNT">
          <SettingRow iconName="person-outline"      label="Edit Profile"     sub="Update your personal info"    onPress={() => {}} />
          <SettingRow iconName="lock-closed-outline" label="Change Password"  sub="Last updated 30 days ago"     onPress={() => {}} last />
        </SectionCard>

        {/* Preferences */}
        <SectionCard title="PREFERENCES">
          <SettingRow
            iconName="scale-outline" label="Weight Unit"
            right={<SegControl options={['kg','lbs']} value={weightUnit} onChange={setWeightUnit} />}
          />
          <SettingRow
            iconName="time-outline" label="Time Format"
            right={<SegControl options={['12hr','24hr']} value={timeFormat} onChange={setTimeFormat} />}
            last
          />
        </SectionCard>

        {/* Reminders */}
        <SectionCard title="REMINDERS">
          {reminders.map((r, i) => (
            <SettingRow
              key={r.id}
              iconName="notifications-outline"
              iconColor={r.enabled ? Colors.accent : '#94A3B8'}
              label={r.label}
              sub={`${r.enabled ? 'Active' : 'Paused'} · ${r.time}`}
              right={
                <Switch
                  value={r.enabled}
                  onValueChange={() => toggleReminder(r.id)}
                  trackColor={{ false: c.border, true: Colors.accent }}
                  thumbColor="#fff"
                />
              }
              last={i === reminders.length - 1}
            />
          ))}
          <TouchableOpacity
            style={[s.addBtn, { borderTopColor: c.border_light }]}
            onPress={() => addReminder({ label: 'Custom Reminder', time: '8:00 AM' })}
          >
            <Icon name="add-circle-outline" size={17} color={Colors.primary} />
            <Text style={s.addBtnText}>Add Reminder</Text>
          </TouchableOpacity>
        </SectionCard>

        {/* Appearance */}
        <SectionCard title="APPEARANCE">
          <SettingRow
            iconName={isDark ? 'moon' : 'sunny'}
            iconColor={isDark ? '#6366F1' : Colors.warning}
            label={isDark ? 'Dark Mode' : 'Light Mode'}
            sub="Switch app theme"
            right={
              <Switch
                value={isDark}
                onValueChange={toggleDark}
                trackColor={{ false: c.border, true: Colors.primary }}
                thumbColor="#fff"
              />
            }
            last
          />
        </SectionCard>

        {/* Security */}
        <SectionCard title="SECURITY">
          <SettingRow
            iconName="timer-outline" label="Session Timeout"
            right={<SegControl options={['5m','15m','30m']} value={timeout_} onChange={setTimeout_} />}
          />
          <SettingRow
            iconName="log-out-outline" iconColor={Colors.danger}
            label="Sign Out" sub="You'll need to sign in again"
            onPress={handleLogout} danger last
          />
        </SectionCard>

        {/* Danger zone */}
        <View style={[s.dangerCard, { backgroundColor: c.card, borderColor: Colors.danger + '30' }]}>
          <TouchableOpacity onPress={() => setShowDeleteModal(true)} style={s.dangerRow}>
            <View style={[s.dangerIconWrap, { backgroundColor: Colors.danger + '14' }]}>
              <Icon name="trash-outline" size={17} color={Colors.danger} />
            </View>
            <View style={s.dangerText}>
              <Text style={s.dangerLabel}>Delete Account</Text>
              <Text style={s.dangerSub}>Permanently remove all your data</Text>
            </View>
            <Icon name="chevron-forward" size={17} color={Colors.danger} />
          </TouchableOpacity>
        </View>

        <View style={{ height: 110 }} />
      </ScrollView>

      {/* Delete confirmation modal */}
      <Modal visible={showDeleteModal} transparent animationType="fade">
        <View style={[s.overlay, { backgroundColor: c.overlay }]}>
          <View style={[s.modal, { backgroundColor: c.card }]}>
            <View style={[s.modalIcon, { backgroundColor: Colors.danger + '14' }]}>
              <Icon name="warning" size={34} color={Colors.danger} />
            </View>
            <Text style={[s.modalTitle, { color: c.text1 }]}>Delete Account?</Text>
            <Text style={[s.modalBody, { color: c.text2 }]}>
              This will permanently delete all your health records, goals, and account data. This cannot be undone.
            </Text>
            <TouchableOpacity
              style={s.deleteBtn}
              onPress={() => { setShowDeleteModal(false); handleLogout(); }}
            >
              <Icon name="trash-outline" size={16} color="#fff" />
              <Text style={s.deleteBtnText}> Yes, Delete Everything</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.keepBtn} onPress={() => setShowDeleteModal(false)}>
              <Text style={[s.keepBtnText, { color: c.text3 }]}>Keep My Account</Text>
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
  headerTitle: { ...Typography.h2, color: '#fff' },
  editBtn:     { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: 'rgba(255,255,255,0.12)', borderRadius: R.md, paddingHorizontal: 12, paddingVertical: 8 },
  editBtnText: { ...Typography.bodySm, color: '#fff', fontWeight: '600' },

  scroll: { padding: S.xl, gap: 14 },

  profileCard:  { alignItems: 'center', paddingTop: S.xxl, paddingBottom: S.lg, gap: 6 },
  avatarWrap:   { position: 'relative', marginBottom: 8 },
  avatar:       { width: 90, height: 90, borderRadius: 45, backgroundColor: Colors.primary, alignItems: 'center', justifyContent: 'center', borderWidth: 3 },
  avatarLetter: { fontSize: 36, fontWeight: '700', color: '#fff' },
  cameraBtn:    { position: 'absolute', bottom: 0, right: 0, width: 28, height: 28, borderRadius: 14, backgroundColor: Colors.accent, alignItems: 'center', justifyContent: 'center', borderWidth: 2 },
  userName:     { ...Typography.h3, marginTop: 4 },
  userEmail:    { ...Typography.bodySm, marginBottom: 8 },
  divider:      { height: 1, width: '100%', marginVertical: 8 },
  statsRow:     { flexDirection: 'row', alignItems: 'center', paddingHorizontal: S.xl, width: '100%', justifyContent: 'space-around' },
  statItem:     { alignItems: 'center', gap: 3, flex: 1 },
  statVal:      { ...Typography.monoSm, fontWeight: '700' },
  statLbl:      { fontSize: 11, fontWeight: '500' },
  statDivider:  { width: 1, height: 32 },

  section:      { gap: 6 },
  sectionLabel: { ...Typography.label, textTransform: 'uppercase', paddingLeft: 4 },

  settingRow:   { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: S.lg, paddingVertical: 13, minHeight: 58 },
  settingIconWrap: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  settingCenter:{ flex: 1 },
  settingLabel: { ...Typography.bodySm, fontWeight: '600' },
  settingSub:   { fontSize: 11, marginTop: 1 },

  seg:          { flexDirection: 'row', borderRadius: R.sm, overflow: 'hidden', borderWidth: 1 },
  segBtn:       { paddingHorizontal: 11, paddingVertical: 7 },
  segTxt:       { ...Typography.label, textTransform: 'none', letterSpacing: 0, fontWeight: '600' },
  segTxtActive: { color: '#fff', fontWeight: '700' },

  addBtn:       { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: S.lg, paddingVertical: 12, borderTopWidth: 1 },
  addBtnText:   { ...Typography.bodySm, color: Colors.primary, fontWeight: '600' },

  dangerCard:   { borderRadius: R.xl, borderWidth: 1, overflow: 'hidden', ...Shadow.sm },
  dangerRow:    { flexDirection: 'row', alignItems: 'center', gap: 12, padding: S.lg },
  dangerIconWrap:{ width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  dangerText:   { flex: 1 },
  dangerLabel:  { ...Typography.bodySm, color: Colors.danger, fontWeight: '600' },
  dangerSub:    { fontSize: 11, color: Colors.danger + 'AA', marginTop: 1 },

  overlay:      { flex: 1, alignItems: 'center', justifyContent: 'center', padding: S.xl },
  modal:        { borderRadius: R.xxl, padding: S.xxl, width: '100%', alignItems: 'center', gap: 10, ...Shadow.lg },
  modalIcon:    { width: 68, height: 68, borderRadius: 34, alignItems: 'center', justifyContent: 'center', marginBottom: 4 },
  modalTitle:   { ...Typography.h3 },
  modalBody:    { ...Typography.bodySm, textAlign: 'center', lineHeight: 22 },
  deleteBtn:    { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: Colors.danger, borderRadius: R.md, paddingVertical: 14, paddingHorizontal: 24, width: '100%', ...Shadow.sm },
  deleteBtnText:{ ...Typography.h4, color: '#fff' },
  keepBtn:      { paddingVertical: 10 },
  keepBtnText:  { ...Typography.bodySm, fontWeight: '600' },
});
