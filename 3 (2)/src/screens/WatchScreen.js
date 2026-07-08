import React, { useState, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  ScrollView, Animated, StatusBar, Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Grad, Typography, S, R, Shadow } from '../theme';
import { useHealth } from '../context/HealthContext';
import { useTheme } from '../context/ThemeContext';
import Icon from '../components/Icon';
import Card from '../components/Card';

const { width: SW } = Dimensions.get('window');

const WATCH_BRANDS = [
  { id: 'apple',   name: 'Apple Watch',          icon: 'watch-outline',        color: '#1C1C1E', metrics: ['Heart Rate', 'SpO₂', 'Steps', 'Sleep', 'ECG'] },
  { id: 'samsung', name: 'Samsung Galaxy Watch',  icon: 'watch-outline',        color: '#1428A0', metrics: ['Heart Rate', 'SpO₂', 'Steps', 'Sleep', 'BP'] },
  { id: 'fitbit',  name: 'Fitbit',                icon: 'fitness-outline',      color: '#00B0B9', metrics: ['Heart Rate', 'Steps', 'Sleep', 'SpO₂', 'Stress'] },
  { id: 'garmin',  name: 'Garmin',                icon: 'compass-outline',      color: '#007CC3', metrics: ['Heart Rate', 'SpO₂', 'Steps', 'Sleep', 'VO₂ Max'] },
];

const SYNC_METRICS = [
  { icon: 'heart',          color: '#EF4444', label: 'Heart Rate',    key: 'heartRate', unit: 'bpm'   },
  { icon: 'heart-circle',   color: '#3B82F6', label: 'Blood Oxygen',  key: 'spO2',      unit: '%'     },
  { icon: 'footsteps',      color: '#10B981', label: 'Steps',         key: 'steps',     unit: 'steps' },
  { icon: 'moon',           color: '#6366F1', label: 'Sleep',         key: 'sleep',     unit: 'hrs'   },
  { icon: 'water',          color: '#06B6D4', label: 'Water Intake',  key: 'water',     unit: 'L'     },
];

function BrandCard({ brand, selected, onSelect }) {
  const { colors: c } = useTheme();
  return (
    <TouchableOpacity
      style={[
        s.brandCard,
        { backgroundColor: c.card, borderColor: selected ? brand.color : c.border_light },
        selected && { borderWidth: 2 },
      ]}
      onPress={() => onSelect(brand)}
      activeOpacity={0.8}
    >
      <View style={[s.brandIconWrap, { backgroundColor: brand.color + '18' }]}>
        <Icon name={brand.icon} size={26} color={brand.color} />
      </View>
      <Text style={[s.brandName, { color: c.text1 }]} numberOfLines={2}>{brand.name}</Text>
      {selected && (
        <View style={[s.brandCheck, { backgroundColor: brand.color }]}>
          <Icon name="checkmark" size={12} color="#fff" />
        </View>
      )}
    </TouchableOpacity>
  );
}

function MetricRow({ metric, value, synced }) {
  const { colors: c } = useTheme();
  return (
    <View style={[s.metricRow, { borderBottomColor: c.border_light }]}>
      <View style={[s.metricIcon, { backgroundColor: metric.color + '18' }]}>
        <Icon name={metric.icon} size={18} color={metric.color} />
      </View>
      <View style={s.metricInfo}>
        <Text style={[s.metricLabel, { color: c.text3 }]}>{metric.label}</Text>
        <Text style={[s.metricValue, { color: c.text1 }]}>
          {value != null ? `${value} ${metric.unit}` : '—'}
        </Text>
      </View>
      {synced && value != null && (
        <View style={[s.syncedBadge, { backgroundColor: Colors.accent + '18' }]}>
          <Icon name="checkmark-circle" size={14} color={Colors.accent} />
          <Text style={[s.syncedText, { color: Colors.accent }]}>Synced</Text>
        </View>
      )}
    </View>
  );
}

export default function WatchScreen({ navigation }) {
  const { colors: c, isDark } = useTheme();
  const { latest, addRecord } = useHealth();

  const [step, setStep]                   = useState('select');   // select | pairing | connected
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [pairingProgress, setPairingProgress] = useState(0);
  const [synced, setSynced]               = useState(false);
  const [lastSync, setLastSync]           = useState(null);
  const pulseAnim  = useRef(new Animated.Value(1)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  const startPulse = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.12, duration: 700, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1,    duration: 700, useNativeDriver: true }),
      ])
    ).start();
  };

  const handleSelectBrand = (brand) => {
    setSelectedBrand(brand);
  };

  const handleStartPairing = () => {
    setStep('pairing');
    startPulse();
    setPairingProgress(0);

    Animated.timing(progressAnim, {
      toValue: 1,
      duration: 3000,
      useNativeDriver: false,
    }).start();

    const interval = setInterval(() => {
      setPairingProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          setStep('connected');
          pulseAnim.stopAnimation();
          return 100;
        }
        return p + 5;
      });
    }, 150);
  };

  const handleSync = () => {
    const now = new Date();
    addRecord({
      weight:    latest.weight    || null,
      systolic:  latest.systolic  || null,
      diastolic: latest.diastolic || null,
      heartRate: latest.heartRate || 72,
      steps:     latest.steps     || 8500,
      sleep:     latest.sleep     || 7.2,
      spO2:      latest.spO2      || 98,
      water:     latest.water     || null,
      notes:     `Auto-synced from ${selectedBrand.name}`,
    });
    setSynced(true);
    setLastSync(now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }));
  };

  const handleDisconnect = () => {
    setStep('select');
    setSelectedBrand(null);
    setSynced(false);
    setLastSync(null);
    progressAnim.setValue(0);
  };

  const renderSelect = () => (
    <>
      <View style={s.heroWrap}>
        <LinearGradient colors={Grad.cta} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={s.heroGrad}>
          <Icon name="watch-outline" size={52} color="rgba(255,255,255,0.9)" />
          <Text style={s.heroTitle}>Connect Your Watch</Text>
          <Text style={s.heroSub}>Automatically sync your health metrics from your wearable device</Text>
        </LinearGradient>
      </View>

      <Text style={[s.sectionTitle, { color: c.text1 }]}>Choose Your Device</Text>
      <View style={s.brandsGrid}>
        {WATCH_BRANDS.map((brand) => (
          <BrandCard
            key={brand.id}
            brand={brand}
            selected={selectedBrand?.id === brand.id}
            onSelect={handleSelectBrand}
          />
        ))}
      </View>

      {selectedBrand && (
        <Card style={s.featuresCard}>
          <Text style={[s.featuresTitle, { color: c.text2 }]}>
            Metrics from {selectedBrand.name}
          </Text>
          <View style={s.featuresList}>
            {selectedBrand.metrics.map((m) => (
              <View key={m} style={[s.featureItem, { backgroundColor: Colors.accent + '12' }]}>
                <Icon name="checkmark-circle" size={14} color={Colors.accent} />
                <Text style={[s.featureText, { color: c.text1 }]}>{m}</Text>
              </View>
            ))}
          </View>
          <TouchableOpacity style={s.connectBtn} onPress={handleStartPairing} activeOpacity={0.85}>
            <LinearGradient colors={Grad.cta} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={s.connectBtnGrad}>
              <Icon name="bluetooth-outline" size={18} color="#fff" />
              <Text style={s.connectBtnText}>Pair {selectedBrand.name}</Text>
            </LinearGradient>
          </TouchableOpacity>
        </Card>
      )}
    </>
  );

  const renderPairing = () => (
    <View style={s.pairingWrap}>
      <Animated.View style={[s.pairingOrb, { transform: [{ scale: pulseAnim }] }]}>
        <LinearGradient colors={Grad.cta} style={s.pairingOrbInner}>
          <Icon name="bluetooth-outline" size={48} color="#fff" />
        </LinearGradient>
      </Animated.View>
      <Text style={[s.pairingTitle, { color: c.text1 }]}>Connecting to</Text>
      <Text style={[s.pairingDevice, { color: Colors.primary }]}>{selectedBrand?.name}</Text>
      <Text style={[s.pairingHint, { color: c.text3 }]}>
        Make sure Bluetooth is on and your watch{'\n'}is nearby
      </Text>
      <View style={[s.progressBar, { backgroundColor: c.border }]}>
        <Animated.View
          style={[
            s.progressFill,
            {
              backgroundColor: Colors.accent,
              width: progressAnim.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }),
            },
          ]}
        />
      </View>
      <Text style={[s.pairingPct, { color: c.text2 }]}>{pairingProgress}%</Text>
    </View>
  );

  const renderConnected = () => (
    <>
      <View style={[s.connectedBanner, { backgroundColor: Colors.accent + '14', borderColor: Colors.accent }]}>
        <View style={[s.connectedIcon, { backgroundColor: Colors.accent }]}>
          <Icon name="checkmark" size={20} color="#fff" />
        </View>
        <View style={s.connectedInfo}>
          <Text style={[s.connectedTitle, { color: c.text1 }]}>{selectedBrand?.name} Connected</Text>
          <Text style={[s.connectedSub, { color: c.text3 }]}>
            {lastSync ? `Last sync: ${lastSync}` : 'Ready to sync'}
          </Text>
        </View>
        <View style={[s.connDot, { backgroundColor: Colors.accent }]} />
      </View>

      <Text style={[s.sectionTitle, { color: c.text1 }]}>Live Metrics</Text>
      <Card>
        {SYNC_METRICS.map((m, i) => (
          <MetricRow
            key={m.key}
            metric={m}
            value={latest[m.key]}
            synced={synced}
          />
        ))}
      </Card>

      <TouchableOpacity style={s.syncBtn} onPress={handleSync} activeOpacity={0.85}>
        <LinearGradient colors={Grad.success} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={s.syncBtnGrad}>
          <Icon name="sync-outline" size={20} color="#fff" />
          <Text style={s.syncBtnText}>Sync Now</Text>
        </LinearGradient>
      </TouchableOpacity>

      <TouchableOpacity style={[s.disconnectBtn, { borderColor: c.border }]} onPress={handleDisconnect}>
        <Icon name="close-circle-outline" size={18} color={Colors.danger} />
        <Text style={[s.disconnectText, { color: Colors.danger }]}>Disconnect Watch</Text>
      </TouchableOpacity>
    </>
  );

  return (
    <View style={[s.root, { backgroundColor: c.bg }]}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      <View style={s.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={s.backBtn}>
          <Icon name="arrow-back" size={22} color={Colors.white} />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Smart Watch</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        contentContainerStyle={s.scroll}
        showsVerticalScrollIndicator={false}
      >
        {step === 'select'    && renderSelect()}
        {step === 'pairing'   && renderPairing()}
        {step === 'connected' && renderConnected()}
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },

  header: {
    backgroundColor: Colors.primary,
    paddingTop: 52, paddingBottom: 16, paddingHorizontal: S.xl,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  backBtn:     { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { ...Typography.h4, color: Colors.white },

  scroll: { padding: S.xl, gap: 16 },

  heroWrap: { borderRadius: R.xl, overflow: 'hidden', ...Shadow.md },
  heroGrad: { padding: S.xxl, alignItems: 'center', gap: 12 },
  heroTitle:{ ...Typography.h3, color: Colors.white, textAlign: 'center' },
  heroSub:  { ...Typography.bodySm, color: 'rgba(255,255,255,0.65)', textAlign: 'center', lineHeight: 20 },

  sectionTitle: { ...Typography.h4, marginBottom: 4 },

  brandsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  brandCard: {
    width: (SW - S.xl * 2 - 10) / 2,
    borderRadius: R.xl, padding: S.lg,
    borderWidth: 1, ...Shadow.sm, alignItems: 'center', gap: 10,
    position: 'relative',
  },
  brandIconWrap: { width: 54, height: 54, borderRadius: R.lg, alignItems: 'center', justifyContent: 'center' },
  brandName:     { ...Typography.bodySm, fontWeight: '600', textAlign: 'center' },
  brandCheck:    { position: 'absolute', top: 10, right: 10, width: 22, height: 22, borderRadius: 11, alignItems: 'center', justifyContent: 'center' },

  featuresCard:   { gap: 14 },
  featuresTitle:  { ...Typography.bodySm, fontWeight: '600' },
  featuresList:   { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  featureItem:    { flexDirection: 'row', alignItems: 'center', gap: 6, borderRadius: R.full, paddingHorizontal: 10, paddingVertical: 5 },
  featureText:    { fontSize: 12, fontWeight: '600' },

  connectBtn:     { borderRadius: R.md, overflow: 'hidden', ...Shadow.md },
  connectBtnGrad: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, paddingVertical: 16 },
  connectBtnText: { ...Typography.h4, color: Colors.white },

  pairingWrap:   { alignItems: 'center', paddingVertical: 40, gap: 16 },
  pairingOrb:    { width: 140, height: 140, borderRadius: 70, overflow: 'hidden', ...Shadow.lg },
  pairingOrbInner:{ flex: 1, alignItems: 'center', justifyContent: 'center' },
  pairingTitle:  { ...Typography.h4 },
  pairingDevice: { ...Typography.h2 },
  pairingHint:   { ...Typography.bodySm, textAlign: 'center', lineHeight: 20 },
  progressBar:   { width: '80%', height: 6, borderRadius: 3, overflow: 'hidden', marginTop: 8 },
  progressFill:  { height: 6, borderRadius: 3 },
  pairingPct:    { ...Typography.bodySm, fontWeight: '600' },

  connectedBanner:{ flexDirection: 'row', alignItems: 'center', gap: 14, borderRadius: R.xl, borderWidth: 1.5, padding: S.lg },
  connectedIcon:  { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  connectedInfo:  { flex: 1, gap: 2 },
  connectedTitle: { ...Typography.h4 },
  connectedSub:   { ...Typography.bodySm },
  connDot:        { width: 10, height: 10, borderRadius: 5 },

  metricRow:    { flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 12, borderBottomWidth: 1 },
  metricIcon:   { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  metricInfo:   { flex: 1, gap: 2 },
  metricLabel:  { fontSize: 11, fontWeight: '600' },
  metricValue:  { ...Typography.monoSm },
  syncedBadge:  { flexDirection: 'row', alignItems: 'center', gap: 4, borderRadius: R.full, paddingHorizontal: 10, paddingVertical: 4 },
  syncedText:   { fontSize: 11, fontWeight: '700' },

  syncBtn:     { borderRadius: R.md, overflow: 'hidden', ...Shadow.md },
  syncBtnGrad: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, paddingVertical: 16 },
  syncBtnText: { ...Typography.h4, color: Colors.white },

  disconnectBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, borderRadius: R.md, borderWidth: 1.5, paddingVertical: 14 },
  disconnectText:{ ...Typography.bodySm, fontWeight: '700' },
});
