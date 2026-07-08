import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, R, Typography } from '../theme';
import { useTheme } from '../context/ThemeContext';

const CFG = {
  good:     { color: Colors.accent,  dot: Colors.accent,  label: 'Good',     bgKey: 'success_bg' },
  normal:   { color: Colors.accent,  dot: Colors.accent,  label: 'Normal',   bgKey: 'success_bg' },
  on_track: { color: Colors.accent,  dot: Colors.accent,  label: 'On Track', bgKey: 'success_bg' },
  watch:    { color: Colors.warning, dot: Colors.warning, label: 'Watch',    bgKey: 'warning_bg' },
  elevated: { color: Colors.warning, dot: Colors.warning, label: 'Elevated', bgKey: 'warning_bg' },
  alert:    { color: Colors.danger,  dot: Colors.danger,  label: 'Alert',    bgKey: 'danger_bg' },
  high:     { color: Colors.danger,  dot: Colors.danger,  label: 'High',     bgKey: 'danger_bg' },
  abnormal: { color: Colors.danger,  dot: Colors.danger,  label: 'Abnormal', bgKey: 'danger_bg' },
};

export default function StatusBadge({ status, size = 'sm' }) {
  const { colors: c } = useTheme();
  const cfg = CFG[status] || CFG.normal;
  const lg  = size === 'lg';
  const bg  = c[cfg.bgKey] || c.success_bg;
  return (
    <View style={[s.wrap, { backgroundColor: bg }, lg && s.wrapLg]}>
      <View style={[s.dot, { backgroundColor: cfg.dot }, lg && s.dotLg]} />
      <Text style={[s.label, { color: cfg.color }, lg && s.labelLg]}>{cfg.label}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  wrap:    { flexDirection: 'row', alignItems: 'center', borderRadius: R.full, paddingHorizontal: 10, paddingVertical: 4 },
  wrapLg:  { paddingHorizontal: 14, paddingVertical: 6 },
  dot:     { width: 6, height: 6, borderRadius: 3, marginRight: 5 },
  dotLg:   { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  label:   { ...Typography.label },
  labelLg: { fontSize: 13, fontWeight: '700', letterSpacing: 0.4 },
});
