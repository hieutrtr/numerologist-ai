const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

// Enable NativeWind v4 CSS processing
module.exports = withNativeWind(config, { input: './global.css' });
