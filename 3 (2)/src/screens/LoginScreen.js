import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from '../components/Icon';
import { Colors, Grad, Typography, S, R, Shadow } from '../theme';

function Input({ icon, placeholder, value, onChangeText, keyboardType, secure, right }) {
  return (
    <View style={s.inputWrap}>
      <Icon name={icon} size={18} color={Colors.text2} style={s.inputIcon} />
      <TextInput
        style={s.input}
        placeholder={placeholder}
        placeholderTextColor={Colors.text3}
        value={value}
        onChangeText={onChangeText}
        keyboardType={keyboardType}
        autoCapitalize="none"
        secureTextEntry={secure}
      />
      {right}
    </View>
  );
}

export default function LoginScreen({ navigation }) {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw]     = useState(false);
  const [mode, setMode]         = useState('login');

  return (
    <View style={s.root}>
      <StatusBar barStyle="light-content" />
      <LinearGradient colors={Grad.header} style={s.heroBg}>
        <View style={s.heroContent}>
          <View style={s.logoRing}>
            <Icon name="heart" size={36} color={Colors.white} />
          </View>
          <Text style={s.appName}>Health Monitor</Text>
          <Text style={s.tagline}>Track · Analyze · Improve</Text>
        </View>
        <View style={s.wave} />
      </LinearGradient>

      <KeyboardAvoidingView
        style={s.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={s.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={s.card}>
            <Text style={s.cardTitle}>
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </Text>
            <Text style={s.cardSub}>
              {mode === 'login' ? 'Sign in to your account' : 'Start tracking your health'}
            </Text>

            <View style={s.fields}>
              <View>
                <Text style={s.label}>Email address</Text>
                <Input
                  icon="mail-outline"
                  placeholder="you@example.com"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                />
              </View>
              <View>
                <Text style={s.label}>Password</Text>
                <Input
                  icon="lock-closed-outline"
                  placeholder="Enter your password"
                  value={password}
                  onChangeText={setPassword}
                  secure={!showPw}
                  right={
                    <TouchableOpacity onPress={() => setShowPw(v => !v)} style={s.eyeBtn}>
                      <Icon
                        name={showPw ? 'eye-off-outline' : 'eye-outline'}
                        size={18}
                        color={Colors.text2}
                      />
                    </TouchableOpacity>
                  }
                />
              </View>
            </View>

            {mode === 'login' && (
              <TouchableOpacity style={s.forgotRow}>
                <Text style={s.forgotText}>Forgot password?</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={s.primaryBtn}
              onPress={() => navigation.replace('Main')}
              activeOpacity={0.87}
            >
              <Text style={s.primaryBtnText}>
                {mode === 'login' ? 'Sign in' : 'Create account'}
              </Text>
              <Icon name="arrow-forward" size={18} color={Colors.white} />
            </TouchableOpacity>

            <View style={s.dividerRow}>
              <View style={s.dividerLine} />
              <Text style={s.dividerText}>or continue with</Text>
              <View style={s.dividerLine} />
            </View>

            <View style={s.socialRow}>
              {['Google', 'Apple'].map(p => (
                <TouchableOpacity key={p} style={s.socialBtn}>
                  <Icon
                    name={p === 'Google' ? 'logo-google' : 'logo-apple'}
                    size={18}
                    color={Colors.text1}
                  />
                  <Text style={s.socialText}>{p}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              onPress={() => setMode(m => m === 'login' ? 'signup' : 'login')}
              style={s.switchRow}
            >
              <Text style={s.switchText}>
                {mode === 'login' ? "Don't have an account?  " : 'Already have an account?  '}
                <Text style={s.switchLink}>
                  {mode === 'login' ? 'Sign up' : 'Sign in'}
                </Text>
              </Text>
            </TouchableOpacity>
          </View>

          <View style={s.badge}>
            <Icon name="shield-checkmark-outline" size={13} color={Colors.text3} />
            <Text style={s.badgeText}>  256-bit encrypted · HIPAA compliant</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const HERO_H = 280;

const s = StyleSheet.create({
  root:       { flex: 1, backgroundColor: Colors.bg },
  flex:       { flex: 1 },
  heroBg:     { height: HERO_H, overflow: 'hidden' },
  heroContent:{ alignItems: 'center', paddingTop: 60 },
  wave:       {
    position: 'absolute', bottom: -40, left: -20, right: -20,
    height: 80, backgroundColor: Colors.bg,
    borderTopLeftRadius: 60, borderTopRightRadius: 60,
  },

  logoRing: {
    width: 72, height: 72, borderRadius: 36,
    backgroundColor: 'rgba(255,255,255,0.15)',
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1.5, borderColor: 'rgba(255,255,255,0.25)',
    marginBottom: 14,
  },
  appName:    { ...Typography.h1, color: Colors.white, marginBottom: 4 },
  tagline:    { fontSize: 13, color: 'rgba(255,255,255,0.6)', letterSpacing: 2 },

  scroll:     { paddingHorizontal: S.xl, paddingBottom: 40 },
  card: {
    backgroundColor: Colors.card,
    borderRadius: R.xxl,
    padding: S.xxl,
    marginTop: -10,
    ...Shadow.lg,
    borderWidth: 1,
    borderColor: Colors.border_light,
  },
  cardTitle:  { ...Typography.h2, color: Colors.text1, marginBottom: 4 },
  cardSub:    { ...Typography.bodySm, color: Colors.text2, marginBottom: 24 },

  fields:     { gap: 14, marginBottom: 6 },
  label:      { ...Typography.label, color: Colors.text2, textTransform: 'uppercase', marginBottom: 6 },
  inputWrap: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: Colors.input_bg,
    borderRadius: R.md,
    borderWidth: 1.5, borderColor: Colors.border,
    paddingHorizontal: 14, height: 52,
  },
  inputIcon:  { marginRight: 10 },
  input:      { flex: 1, ...Typography.body, color: Colors.text1, padding: 0 },
  eyeBtn:     { padding: 4 },

  forgotRow:  { alignItems: 'flex-end', marginTop: 6, marginBottom: 20 },
  forgotText: { ...Typography.bodySm, color: Colors.primary, fontWeight: '600' },

  primaryBtn: {
    backgroundColor: Colors.primary,
    borderRadius: R.md, height: 52,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 8, marginTop: 4,
    ...Shadow.md,
  },
  primaryBtnText: { ...Typography.h4, color: Colors.white },

  dividerRow:  { flexDirection: 'row', alignItems: 'center', marginVertical: 20, gap: 12 },
  dividerLine: { flex: 1, height: 1, backgroundColor: Colors.border },
  dividerText: { ...Typography.bodySm, color: Colors.text3 },

  socialRow:  { flexDirection: 'row', gap: 12, marginBottom: 20 },
  socialBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    borderRadius: R.md, borderWidth: 1.5, borderColor: Colors.border,
    paddingVertical: 12, gap: 8, backgroundColor: Colors.input_bg,
  },
  socialText: { ...Typography.bodySm, fontWeight: '600', color: Colors.text1 },

  switchRow:  { alignItems: 'center' },
  switchText: { ...Typography.bodySm, color: Colors.text2 },
  switchLink: { color: Colors.primary, fontWeight: '700' },

  badge:      { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 20 },
  badgeText:  { ...Typography.label, color: Colors.text3, textTransform: 'none', letterSpacing: 0.2 },
});
