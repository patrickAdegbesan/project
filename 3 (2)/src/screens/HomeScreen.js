import React, { useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Dimensions, StatusBar, Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Grad, Typography, S, R, Shadow } from '../theme';
import { useHealth, getOverallStatus } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import { MiniLineChart } from '../components/MiniChart';
import StatusBadge from '../components/StatusBadge';
import Card from '../components/Card';
import Icon from '../components/Icon';

const { width: SW } = Dimensions.get('window');

const STATUS_CLR = {
  good:  { bg: '#ECFDF5', border: Colors.accent,   icon: 'checkmark-circle', iconColor: Colors.accent },
  watch: { bg: '#FFFBEB', border: Colors.warning,  icon: 'warning',          iconColor: Colors.warning },
  alert: { bg: '#FEF2F2', border: Colors.danger,   icon: 'alert-circle',     iconColor: Colors.danger },
};
const STATUS_CLR_DARK = {
  good:  { bg: 'rgba(0,184,148,0.12)',  border: Colors.accent,  icon: 'checkmark-circle', iconColor: Colors.accent },
  watch: { bg: 'rgba(245,158,11,0.12)', border: Colors.warning, icon: 'warning',          iconColor: Colors.warning },
  alert: { bg: 'rgba(239,68,68,0.12)',  border: Colors.danger,  icon: 'alert-circle',     iconColor: Colors.danger },
};

// ── Sub-components ────────────────────────────────────────────────────────────
function StatCard({ iconName, value, label, sub, subColor, trend }) {
  const { colors: c } = useTheme();
  return (
    <View style={[s.statCard, { backgroundColor: c.card, borderColor: c.border_light }]}>
      <View style={[s.statIconWrap, { backgroundColor: Colors.primary + '14' }]}>
        <Icon name={iconName} size={18} color={Colors.primary} />
      </View>
      <Text style={[s.statValue, { color: c.text1 }]}>{value}</Text>
      <Text style={[s.statLabel, { color: c.text3 }]}>{label}</Text>
      {sub ? (
        <View style={s.statSubRow}>
          {trend && <Icon name={trend === 'up' ? 'trending-up' : 'trending-down'} size={11} color={subColor} />}
          <Text style={[s.statSub, { color: subColor }]}>{sub}</Text>
        </View>
      ) : null}
    </View>
  );
}

function ActivityCard({ iconName, iconColor, value, label, pct, barColor }) {
  const { colors: c } = useTheme();
  return (
    <View style={[s.actCard, { backgroundColor: c.card, borderColor: c.border_light }]}>
      <View style={[s.actCardIcon, { backgroundColor: iconColor + '18' }]}>
        <Icon name={iconName} size={18} color={iconColor} />
      </View>
      <Text style={[s.actCardVal, { color: c.text1 }]}>{value}</Text>
      <Text style={[s.actCardLabel, { color: c.text3 }]}>{label}</Text>
      {pct != null && (
        <View style={[s.actBar, { backgroundColor: c.border }]}>
          <View style={[s.actBarFill, { width: `${Math.min(100, pct)}%`, backgroundColor: barColor || iconColor }]} />
        </View>
      )}
    </View>
  );
}

function ActivityRow({ record }) {
  const { colors: c } = useTheme();
  const status = getOverallStatus(record);
  const date   = new Date(record.date);
  const diff   = Math.round((Date.now() - date) / 86400000);
  const label  = diff === 0 ? 'Today' : diff === 1 ? 'Yesterday' : `${diff}d ago`;
  return (
    <View style={[s.actRow, { borderBottomColor: c.border_light }]}>
      <View style={s.actLeft}>
        <View style={s.actDateWrap}>
          <Icon name="calendar-outline" size={12} color={c.text3} />
          <Text style={[s.actDate, { color: c.text3 }]}>{label}</Text>
        </View>
        <Text style={[s.actValues, { color: c.text1 }]}>
          {record.weight ? `${record.weight} kg` : '— kg'}
          {'  ·  '}
          {record.systolic ? `${record.systolic}/${record.diastolic}` : '—/—'}
          {'  ·  '}
          {record.heartRate ? `${record.heartRate} bpm` : '— bpm'}
        </Text>
      </View>
      <StatusBadge status={status} />
    </View>
  );
}

function NotificationsPanel({ visible, onClose }) {
  const { colors: c } = useTheme();
  const { notifications, markNotificationsRead } = useHealth();

  const handleClose = () => { markNotificationsRead(); onClose(); };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <TouchableOpacity style={[s.notifOverlay, { backgroundColor: c.overlay }]} activeOpacity={1} onPress={handleClose} />
      <View style={[s.notifPanel, { backgroundColor: c.card, borderColor: c.border_light }]}>
        <View style={[s.notifPanelHeader, { borderBottomColor: c.border_light }]}>
          <Text style={[s.notifPanelTitle, { color: c.text1 }]}>Notifications</Text>
          <TouchableOpacity onPress={handleClose} style={[s.notifCloseBtn, { backgroundColor: c.border_light }]}>
            <Icon name="close" size={16} color={c.text2} />
          </TouchableOpacity>
        </View>
        <ScrollView showsVerticalScrollIndicator={false}>
          {notifications.map((n, i) => (
            <View key={n.id} style={[
              s.notifItem,
              { borderBottomColor: c.border_light },
              !n.read && { backgroundColor: n.color + '0A' },
            ]}>
              <View style={[s.notifItemIcon, { backgroundColor: n.color + '18' }]}>
                <Icon name={n.icon} size={18} color={n.color} />
              </View>
              <View style={s.notifItemBody}>
                <View style={s.notifItemTop}>
                  <Text style={[s.notifItemTitle, { color: c.text1 }]}>{n.title}</Text>
                  {!n.read && <View style={[s.notifUnreadDot, { backgroundColor: Colors.accent }]} />}
                </View>
                <Text style={[s.notifItemText, { color: c.text2 }]}>{n.body}</Text>
                <Text style={[s.notifItemTime, { color: c.text3 }]}>{n.time}</Text>
              </View>
            </View>
          ))}
        </ScrollView>
      </View>
    </Modal>
  );
}

// ── Main screen ───────────────────────────────────────────────────────────────
export default function HomeScreen({ navigation }) {
  const { colors: c, isDark } = useTheme();
  const { records, latest, streak, user, unreadCount } = useHealth();
  const [showNotif, setShowNotif] = useState(false);

  const overall    = latest ? getOverallStatus(latest) : 'good';
  const statusCfg  = (isDark ? STATUS_CLR_DARK : STATUS_CLR)[overall] || (isDark ? STATUS_CLR_DARK : STATUS_CLR).good;
  const weightData = [...records].slice(0, 14).reverse().map(r => r.weight);
  const days       = ['M','T','W','T','F','S','S'];

  const stepPct   = Math.min(100, ((latest.steps  || 0) / 10000) * 100);
  const sleepPct  = Math.min(100, ((latest.sleep  || 0) / 8)    * 100);
  const waterPct  = Math.min(100, ((latest.water  || 0) / 2.5)  * 100);

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      {/* ── Header ── */}
      <View style={s.header}>
        <View style={s.headerTop}>
          <View>
            <Text style={s.greeting}>Good morning</Text>
            <Text style={s.userName}>{user.name}</Text>
          </View>
          <View style={s.headerRight}>
            <TouchableOpacity style={s.notifBtn} onPress={() => setShowNotif(true)} activeOpacity={0.8}>
              <Icon name="notifications-outline" size={22} color={Colors.white} />
              {unreadCount > 0 && (
                <View style={s.notifBadge}>
                  <Text style={s.notifBadgeText}>{unreadCount}</Text>
                </View>
              )}
            </TouchableOpacity>
            <TouchableOpacity
              style={s.avatar}
              onPress={() => navigation.navigate('Profile')}
              activeOpacity={0.8}
            >
              <Text style={s.avatarText}>{user.name.charAt(0)}</Text>
            </TouchableOpacity>
          </View>
        </View>
        <Text style={s.headerDate}>
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={s.scroll}>

        {/* ── Vitals stat cards ── */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.statsScroll} contentContainerStyle={s.statsRow}>
          <StatCard iconName="scale-outline"   value={`${latest.weight || '—'}`}  label="Weight (kg)" sub="↓ Trending" subColor={Colors.accent} trend="down" />
          <StatCard iconName="heart-outline"   value={`${latest.systolic || '—'}/${latest.diastolic || '—'}`} label="Blood Pressure" sub="Normal" subColor={Colors.accent} />
          <StatCard iconName="pulse-outline"   value={`${latest.heartRate || '—'}`} label="HR (bpm)" sub="Resting" subColor={c.text2} />
          <StatCard iconName="flame-outline"   value={`${streak}`} label="Day Streak" sub="Personal best!" subColor={Colors.warning} />
        </ScrollView>

        {/* ── Overall status ── */}
        <TouchableOpacity
          style={[s.statusCard, { backgroundColor: statusCfg.bg, borderColor: statusCfg.border }]}
          onPress={() => navigation.navigate('Trends')}
          activeOpacity={0.85}
        >
          <View style={[s.statusIconWrap, { backgroundColor: statusCfg.iconColor + '18' }]}>
            <Icon name={statusCfg.icon} size={28} color={statusCfg.iconColor} />
          </View>
          <View style={s.statusText}>
            <Text style={[s.statusTitle, { color: c.text2 }]}>Overall Health Status</Text>
            <StatusBadge status={overall} size="lg" />
          </View>
          <Icon name="chevron-forward" size={18} color={c.text3} />
        </TouchableOpacity>

        {/* ── Log CTA ── */}
        <TouchableOpacity onPress={() => navigation.navigate('LogHealth')} activeOpacity={0.88}>
          <LinearGradient colors={Grad.cta} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={s.logCTA}>
            <View style={s.logCTALeft}>
              <View style={s.logCTAIconWrap}>
                <Icon name="add-circle" size={32} color={Colors.white} />
              </View>
              <View>
                <Text style={s.logCTATitle}>Log Today's Vitals</Text>
                <Text style={s.logCTASub}>Weight · BP · Heart Rate · Steps</Text>
              </View>
            </View>
            <Icon name="arrow-forward-circle-outline" size={26} color="rgba(255,255,255,0.7)" />
          </LinearGradient>
        </TouchableOpacity>

        {/* ── Watch CTA ── */}
        <TouchableOpacity
          style={[s.watchCTA, { backgroundColor: c.card, borderColor: c.border_light }]}
          onPress={() => navigation.navigate('Watch')}
          activeOpacity={0.85}
        >
          <View style={[s.watchCTAIcon, { backgroundColor: Colors.primary + '14' }]}>
            <Icon name="watch-outline" size={22} color={Colors.primary} />
          </View>
          <View style={s.watchCTAText}>
            <Text style={[s.watchCTATitle, { color: c.text1 }]}>Connect Smart Watch</Text>
            <Text style={[s.watchCTASub, { color: c.text3 }]}>Sync Apple Watch · Garmin · Fitbit · Samsung</Text>
          </View>
          <Icon name="chevron-forward" size={18} color={c.text3} />
        </TouchableOpacity>

        {/* ── Today's Activity (watch metrics) ── */}
        <View>
          <Text style={[s.sectionTitle, { color: c.text1 }]}>Today's Activity</Text>
          <View style={s.actGrid}>
            <ActivityCard iconName="footsteps"   iconColor="#10B981" value={`${(latest.steps || 0).toLocaleString()}`} label="Steps" pct={stepPct} />
            <ActivityCard iconName="moon-outline" iconColor="#6366F1" value={`${latest.sleep || '—'} h`} label="Sleep" pct={sleepPct} barColor="#6366F1" />
            <ActivityCard iconName="water"        iconColor="#06B6D4" value={`${latest.water || '—'} L`} label="Water" pct={waterPct} barColor="#06B6D4" />
            <ActivityCard iconName="heart-circle-outline" iconColor={latest.spO2 >= 97 ? Colors.accent : Colors.warning} value={`${latest.spO2 || '—'}%`} label="SpO₂" />
          </View>
        </View>

        {/* ── Weight chart ── */}
        <Card style={s.chartCard}>
          <View style={s.chartHeader}>
            <View>
              <Text style={[s.sectionTitle, { color: c.text1 }]}>Weight Trend</Text>
              <Text style={[s.chartSub, { color: c.text3 }]}>Last 14 days</Text>
            </View>
            <View style={[s.chartBadge, { backgroundColor: c.success_bg }]}>
              <Icon name="trending-down" size={13} color={Colors.accent} />
              <Text style={s.chartBadgeText}> {latest.weight} kg</Text>
            </View>
          </View>
          <MiniLineChart
            data={weightData}
            width={Math.max(100, SW - 74)}
            height={90}
            color={isDark ? Colors.accent : Colors.primary}
          />
          <View style={s.chartLabels}>
            {days.map((d, i) => <Text key={i} style={[s.chartLabel, { color: c.text3 }]}>{d}</Text>)}
          </View>
        </Card>

        {/* ── Recent Activity ── */}
        <Card>
          <View style={s.sectionHeader}>
            <Text style={[s.sectionTitle, { color: c.text1 }]}>Recent Activity</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Trends')} style={s.seeAllBtn}>
              <Text style={s.seeAll}>See all</Text>
              <Icon name="chevron-forward" size={14} color={Colors.primary} />
            </TouchableOpacity>
          </View>
          {records.slice(0, 3).map((r, i) => (
            <React.Fragment key={r.id}>
              {i > 0 && <View style={[s.divider, { backgroundColor: c.border_light }]} />}
              <ActivityRow record={r} />
            </React.Fragment>
          ))}
        </Card>

        <View style={{ height: 110 }} />
      </ScrollView>

      <NotificationsPanel visible={showNotif} onClose={() => setShowNotif(false)} />
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },

  header: {
    backgroundColor: Colors.primary,
    paddingTop: 52, paddingHorizontal: S.xl, paddingBottom: 24,
  },
  headerTop:  { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 },
  greeting:   { ...Typography.bodySm, color: 'rgba(255,255,255,0.6)', marginBottom: 2 },
  userName:   { ...Typography.h2, color: Colors.white },
  headerDate: { ...Typography.bodySm, color: 'rgba(255,255,255,0.5)' },
  headerRight:{ flexDirection: 'row', alignItems: 'center', gap: 12 },
  notifBtn:   { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center', position: 'relative' },
  notifBadge: { position: 'absolute', top: 6, right: 6, minWidth: 16, height: 16, borderRadius: 8, backgroundColor: Colors.danger, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 3, borderWidth: 1.5, borderColor: Colors.primary },
  notifBadgeText: { fontSize: 9, color: '#fff', fontWeight: '700' },
  avatar:     { width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.accent, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: 'rgba(255,255,255,0.3)' },
  avatarText: { ...Typography.h4, color: Colors.white },

  scroll: { padding: S.xl, gap: 14 },

  statsScroll: { marginHorizontal: -S.xl },
  statsRow:    { paddingHorizontal: S.xl, gap: 10 },
  statCard: {
    width: 122, borderRadius: R.xl, padding: S.md,
    ...Shadow.sm, borderWidth: 1,
  },
  statIconWrap: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center', marginBottom: 10 },
  statValue:    { ...Typography.monoSm, marginBottom: 2 },
  statLabel:    { fontSize: 11, fontWeight: '500', marginBottom: 4 },
  statSubRow:   { flexDirection: 'row', alignItems: 'center', gap: 3 },
  statSub:      { fontSize: 11, fontWeight: '600' },

  statusCard: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    borderRadius: R.xl, borderWidth: 1.5, padding: S.lg, ...Shadow.xs,
  },
  statusIconWrap: { width: 52, height: 52, borderRadius: R.lg, alignItems: 'center', justifyContent: 'center' },
  statusText:     { flex: 1, gap: 6 },
  statusTitle:    { ...Typography.bodySm, fontWeight: '600' },

  logCTA: {
    borderRadius: R.xl, padding: S.lg,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', ...Shadow.md,
  },
  logCTALeft:    { flexDirection: 'row', alignItems: 'center', gap: 14 },
  logCTAIconWrap:{ width: 48, height: 48, borderRadius: 14, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center' },
  logCTATitle:   { ...Typography.h4, color: Colors.white, marginBottom: 2 },
  logCTASub:     { fontSize: 11, color: 'rgba(255,255,255,0.55)', fontWeight: '400' },

  sectionTitle:  { ...Typography.h4, marginBottom: 4 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  seeAllBtn:     { flexDirection: 'row', alignItems: 'center', gap: 2 },
  seeAll:        { ...Typography.bodySm, color: Colors.primary, fontWeight: '600' },

  actGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 6 },
  actCard: {
    width: (SW - S.xl * 2 - 10) / 2,
    borderRadius: R.xl, padding: S.md, borderWidth: 1, ...Shadow.sm, gap: 4,
  },
  actCardIcon:  { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center', marginBottom: 4 },
  actCardVal:   { ...Typography.monoSm, fontWeight: '700' },
  actCardLabel: { fontSize: 11, fontWeight: '500' },
  actBar:       { height: 4, borderRadius: 2, marginTop: 6, overflow: 'hidden' },
  actBarFill:   { height: 4, borderRadius: 2 },

  chartCard:    { paddingBottom: S.sm },
  chartHeader:  { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 },
  chartSub:     { fontSize: 11, fontWeight: '400', marginTop: 2 },
  chartBadge:   { flexDirection: 'row', alignItems: 'center', borderRadius: R.full, paddingHorizontal: 10, paddingVertical: 5 },
  chartBadgeText: { ...Typography.monoXs, color: Colors.accent },
  chartLabels:  { flexDirection: 'row', justifyContent: 'space-around', marginTop: 6, paddingHorizontal: 4 },
  chartLabel:   { fontSize: 11, fontWeight: '500' },

  divider:   { height: 1, marginVertical: 2 },
  actRow:    { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 10 },
  actLeft:   { flex: 1, marginRight: 12, gap: 4 },
  actDateWrap: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  actDate:   { fontSize: 11, fontWeight: '600' },
  actValues: { ...Typography.bodySm, fontWeight: '500' },

  watchCTA: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    borderRadius: R.xl, borderWidth: 1, padding: S.lg, ...Shadow.xs,
  },
  watchCTAIcon:  { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  watchCTAText:  { flex: 1, gap: 3 },
  watchCTATitle: { ...Typography.h4 },
  watchCTASub:   { fontSize: 11, fontWeight: '500' },

  // Notification panel
  notifOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  notifPanel: {
    position: 'absolute', top: 90, right: S.xl, width: Math.min(340, SW - S.xl * 2),
    borderRadius: R.xl, borderWidth: 1, maxHeight: 420, ...Shadow.lg, overflow: 'hidden',
  },
  notifPanelHeader: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: S.lg, paddingVertical: S.md, borderBottomWidth: 1,
  },
  notifPanelTitle:  { ...Typography.h4 },
  notifCloseBtn:    { width: 28, height: 28, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  notifItem:        { flexDirection: 'row', gap: 12, padding: S.lg, borderBottomWidth: 1 },
  notifItemIcon:    { width: 38, height: 38, borderRadius: 10, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  notifItemBody:    { flex: 1, gap: 2 },
  notifItemTop:     { flexDirection: 'row', alignItems: 'center', gap: 6 },
  notifItemTitle:   { ...Typography.bodySm, fontWeight: '700', flex: 1 },
  notifUnreadDot:   { width: 7, height: 7, borderRadius: 3.5 },
  notifItemText:    { ...Typography.bodySm, lineHeight: 18 },
  notifItemTime:    { fontSize: 11, fontWeight: '500', marginTop: 2 },
});
