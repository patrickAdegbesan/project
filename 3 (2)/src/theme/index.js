const base = {
  primary:      '#0A2E36',
  primary_mid:  '#1A4A5A',
  primary_light:'#2A6478',
  accent:       '#00B894',
  accent_light: '#00D4AA',
  warning:      '#F59E0B',
  danger:       '#EF4444',
  chart_teal:   '#0A2E36',
  chart_sys:    '#EF4444',
  chart_dia:    '#3B82F6',
  chart_hr:     '#00B894',
  white:        '#FFFFFF',
};

export const LightColors = {
  ...base,
  bg:           '#F0F4F8',
  card:         '#FFFFFF',
  border:       '#E2E8F0',
  border_light: '#F1F5F9',
  input_bg:     '#F8FAFC',
  text1:        '#0F172A',
  text2:        '#475569',
  text3:        '#94A3B8',
  warning_bg:   '#FFFBEB',
  danger_bg:    '#FEF2F2',
  success_bg:   '#ECFDF5',
  healthy_fill: 'rgba(0,184,148,0.08)',
  chart_fill:   'rgba(10,46,54,0.08)',
  overlay:      'rgba(15,23,42,0.6)',
};

export const DarkColors = {
  ...base,
  bg:           '#0D1B2A',
  card:         '#152232',
  border:       '#1E3348',
  border_light: '#1A2D40',
  input_bg:     '#0F2030',
  text1:        '#F1F5F9',
  text2:        '#94A3B8',
  text3:        '#4E6680',
  warning_bg:   'rgba(245,158,11,0.12)',
  danger_bg:    'rgba(239,68,68,0.12)',
  success_bg:   'rgba(0,184,148,0.12)',
  healthy_fill: 'rgba(0,184,148,0.06)',
  chart_fill:   'rgba(0,184,148,0.06)',
  overlay:      'rgba(0,0,0,0.75)',
};

// Static fallback (used in StyleSheet.create calls — always light)
export const Colors = LightColors;

export const Grad = {
  header:  ['#0A2E36', '#1A4A5A'],
  cta:     ['#0A2E36', '#2A6478'],
  success: ['#00B894', '#00D4AA'],
  danger:  ['#EF4444', '#F87171'],
};

export const Typography = {
  h1:     { fontSize: 28, fontWeight: '700', letterSpacing: -0.5 },
  h2:     { fontSize: 22, fontWeight: '700', letterSpacing: -0.3 },
  h3:     { fontSize: 18, fontWeight: '700' },
  h4:     { fontSize: 16, fontWeight: '600' },
  body:   { fontSize: 15, fontWeight: '400', lineHeight: 22 },
  bodySm: { fontSize: 13, fontWeight: '400', lineHeight: 20 },
  label:  { fontSize: 11, fontWeight: '600', letterSpacing: 0.8 },
  mono:   { fontFamily: 'Courier', fontSize: 22, fontWeight: '700' },
  monoSm: { fontFamily: 'Courier', fontSize: 17, fontWeight: '600' },
  monoXs: { fontFamily: 'Courier', fontSize: 13, fontWeight: '500' },
};

export const S = { xs: 4, sm: 8, md: 12, lg: 16, xl: 20, xxl: 28 };
export const R = { sm: 8, md: 12, lg: 16, xl: 20, xxl: 24, full: 999 };

export const Shadow = {
  xs: { shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.06, shadowRadius: 4,  elevation: 1 },
  sm: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 8,  elevation: 2 },
  md: { shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.10, shadowRadius: 12, elevation: 4 },
  lg: { shadowColor: '#000', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.14, shadowRadius: 20, elevation: 8 },
};

export const TAB_H = 68;
