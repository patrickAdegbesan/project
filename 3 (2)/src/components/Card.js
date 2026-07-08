import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { R, Shadow, S } from '../theme';

export default function Card({ children, style, pad = true }) {
  const { colors: c } = useTheme();
  return (
    <View style={[
      s.card,
      { backgroundColor: c.card, borderColor: c.border_light },
      pad && s.pad,
      Shadow.sm,
      style,
    ]}>
      {children}
    </View>
  );
}

const s = StyleSheet.create({
  card: { borderRadius: R.xl, borderWidth: 1 },
  pad:  { padding: S.lg },
});
