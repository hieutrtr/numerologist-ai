const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// NativeWind v4 with Expo - the preset handles CSS processing
// No need for explicit metro integration in Expo 54+
module.exports = config;
