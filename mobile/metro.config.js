const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Try to add NativeWind if available, otherwise use default config
try {
  const { withNativeWind } = require('nativewind/metro');
  module.exports = withNativeWind(config, { input: './global.css' });
} catch (e) {
  // Fallback to default config if NativeWind is not available
  console.warn('[metro.config] NativeWind not available, using default config');
  module.exports = config;
}
