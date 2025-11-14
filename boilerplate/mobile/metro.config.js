const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

// Enable NativeWind v4 CSS processing
// This wraps Metro to process Tailwind CSS classes
module.exports = withNativeWind(config, { input: './global.css' });
