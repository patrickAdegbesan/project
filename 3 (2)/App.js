import 'react-native-gesture-handler';
import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { HealthProvider } from './src/context/HealthContext';
import { ThemeProvider } from './src/context/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <HealthProvider>
          <AppNavigator />
        </HealthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
