import React from 'react';
import { Ionicons } from '@expo/vector-icons';

export default function Icon({ name, size = 22, color = '#000', style }) {
  return <Ionicons name={name} size={size} color={color} style={style} />;
}
