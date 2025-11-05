import { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ActivityIndicator, Pressable } from 'react-native';
import { apiClient, HealthCheckResponse } from '@/services/api';

export default function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<HealthCheckResponse | null>(null);

  const checkHealth = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get<HealthCheckResponse>('/health');

      setHealthData(response.data);
      setConnected(response.data.status === 'healthy');
    } catch (err) {
      setConnected(false);
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Numerologist AI</Text>

      <View style={styles.statusContainer}>
        {loading ? (
          <>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.statusText}>Checking connection...</Text>
          </>
        ) : connected ? (
          <>
            <Text style={[styles.statusText, styles.connected]}>
              ✓ API Status: Connected
            </Text>
            {healthData && (
              <View style={styles.details}>
                <Text style={styles.detailText}>
                  Database: {healthData.database}
                </Text>
                <Text style={styles.detailText}>
                  Redis: {healthData.redis}
                </Text>
              </View>
            )}
          </>
        ) : (
          <>
            <Text style={[styles.statusText, styles.error]}>
              ✗ API Status: {error}
            </Text>
            <Pressable style={styles.retryButton} onPress={checkHealth}>
              <Text style={styles.retryText}>Retry Connection</Text>
            </Pressable>
          </>
        )}
      </View>

      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 40,
  },
  statusContainer: {
    alignItems: 'center',
    padding: 20,
    borderRadius: 12,
    backgroundColor: '#f5f5f5',
    minWidth: 300,
  },
  statusText: {
    fontSize: 18,
    marginTop: 10,
  },
  connected: {
    color: '#34C759',
    fontWeight: '600',
  },
  error: {
    color: '#FF3B30',
    fontWeight: '600',
  },
  details: {
    marginTop: 15,
    alignItems: 'flex-start',
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginVertical: 2,
  },
  retryButton: {
    marginTop: 15,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  retryText: {
    color: '#fff',
    fontWeight: '600',
  },
});
