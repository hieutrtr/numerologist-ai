/**
 * Connection Status Component
 *
 * Displays the current connection status and bot presence.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ConnectionStatusProps {
  isConnected: boolean;
  isBotPresent: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  isBotPresent,
}) => {
  const getStatusColor = () => {
    if (!isConnected) return '#999999';
    if (isBotPresent) return '#34C759';
    return '#FF9500';
  };

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';
    if (isBotPresent) return 'Connected';
    return 'Connecting...';
  };

  return (
    <View style={styles.container}>
      <View style={[styles.indicator, { backgroundColor: getStatusColor() }]} />
      <Text style={[styles.text, { color: getStatusColor() }]}>
        {getStatusText()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  indicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  text: {
    fontSize: 14,
    fontWeight: '500',
  },
});

export default ConnectionStatus;
