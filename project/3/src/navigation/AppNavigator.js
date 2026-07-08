import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { NavigationContainer, DarkTheme, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Colors, Typography, TAB_H, Shadow } from '../theme';
import { useTheme } from '../context/ThemeContext';
import Icon from '../components/Icon';

import LoginScreen     from '../screens/LoginScreen';
import HomeScreen      from '../screens/HomeScreen';
import LogHealthScreen from '../screens/LogHealthScreen';
import TrendsScreen    from '../screens/TrendsScreen';
import GoalsScreen     from '../screens/GoalsScreen';
import ProfileScreen   from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab   = createBottomTabNavigator();

const TABS = [
  { name: 'Home',      label: 'Home',   icon: 'heart-outline',  iconActive: 'heart' },
  { name: 'Trends',   label: 'Trends', icon: 'pulse-outline',  iconActive: 'pulse-outline' },
  { name: 'LogHealth',label: 'Log',    icon: 'add',             isCTA: true },
  { name: 'Goals',    label: 'Goals',  icon: 'trophy-outline',  iconActive: 'trophy-outline' },
  { name: 'Profile',  label: 'Profile',icon: 'person-outline',  iconActive: 'person-outline' },
];

function CustomTabBar({ state, navigation }) {
  const insets      = useSafeAreaInsets();
  const { colors: c } = useTheme();

  return (
    <View style={[
      s.bar,
      { backgroundColor: c.card, borderTopColor: c.border_light, paddingBottom: Math.max(insets.bottom, 10) },
      Shadow.md,
    ]}>
      {TABS.map((tab, i) => {
        const focused  = state.index === i;
        const onPress  = () => navigation.navigate(tab.name);

        if (tab.isCTA) {
          return (
            <TouchableOpacity key={tab.name} style={s.ctaWrap} onPress={onPress} activeOpacity={0.85}>
              <View style={[s.ctaBtn, { borderColor: c.card }]}>
                <Icon name="add" size={24} color="#fff" />
              </View>
              <Text style={[s.ctaLabel, { color: c.text3 }]}>{tab.label}</Text>
            </TouchableOpacity>
          );
        }

        return (
          <TouchableOpacity key={tab.name} style={s.tabItem} onPress={onPress} activeOpacity={0.75}>
            {focused && <View style={s.activePill} />}
            <Icon
              name={focused ? (tab.iconActive || tab.icon) : tab.icon}
              size={22}
              color={focused ? Colors.primary : c.text3}
            />
            <Text style={[s.tabLabel, { color: focused ? Colors.primary : c.text3 }, focused && s.tabLabelActive]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      tabBar={props => <CustomTabBar {...props} />}
      screenOptions={{ headerShown: false }}
    >
      <Tab.Screen name="Home"      component={HomeScreen} />
      <Tab.Screen name="Trends"    component={TrendsScreen} />
      <Tab.Screen name="LogHealth" component={LogHealthScreen} />
      <Tab.Screen name="Goals"     component={GoalsScreen} />
      <Tab.Screen name="Profile"   component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { isDark } = useTheme();
  const navTheme = isDark
    ? { ...DarkTheme,    colors: { ...DarkTheme.colors,    background: '#0D1B2A' } }
    : { ...DefaultTheme, colors: { ...DefaultTheme.colors, background: '#F0F4F8' } };

  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Login">
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Main"  component={MainTabs} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const s = StyleSheet.create({
  bar: { flexDirection: 'row', borderTopWidth: 1, paddingTop: 8, minHeight: TAB_H },
  tabItem:      { flex: 1, alignItems: 'center', justifyContent: 'flex-start', paddingTop: 4, position: 'relative' },
  activePill:   { position: 'absolute', top: -8, width: 36, height: 3, backgroundColor: Colors.primary, borderRadius: 2 },
  tabLabel:     { fontSize: 11, fontWeight: '500', marginTop: 4 },
  tabLabelActive:{ fontWeight: '700' },
  ctaWrap: { flex: 1, alignItems: 'center', justifyContent: 'flex-start', paddingTop: 0 },
  ctaBtn: {
    width: 50, height: 50, borderRadius: 25,
    backgroundColor: Colors.primary,
    alignItems: 'center', justifyContent: 'center',
    marginTop: -18, borderWidth: 3,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.45, shadowRadius: 10, elevation: 8,
  },
  ctaLabel: { fontSize: 11, fontWeight: '500', marginTop: 4 },
});
