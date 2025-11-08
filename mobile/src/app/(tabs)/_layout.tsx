import React from 'react';
import { Tabs } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Tabs Layout Component
 *
 * Creates a bottom tab navigation for authenticated users with three screens:
 * - Conversation (Home) - index.tsx
 * - History - history.tsx
 * - Profile - profile.tsx
 *
 * This layout is automatically displayed to authenticated users
 * after they login via the root layout conditional rendering.
 */
export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#d4af37', // primary gold
        tabBarInactiveTintColor: '#6b7280', // text-muted
        tabBarStyle: {
          backgroundColor: '#0d0d1a', // bg-dark
          borderTopWidth: 1,
          borderTopColor: '#333', // border-DEFAULT
          paddingBottom: 5,
          paddingTop: 5,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      }}
    >
      {/* Conversation/Home Tab */}
      <Tabs.Screen
        name="index"
        options={{
          title: 'Conversation',
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="chat" color={color} size={size} />
          ),
        }}
      />

      {/* History Tab */}
      <Tabs.Screen
        name="history"
        options={{
          title: 'History',
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="history" color={color} size={size} />
          ),
        }}
      />

      {/* Profile Tab */}
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialIcons name="person" color={color} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}
