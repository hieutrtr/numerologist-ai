module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      // Expo preset with NativeWind support
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      // NativeWind preset for Tailwind CSS support
      "nativewind/babel",
    ],
    plugins: [
      // Reanimated plugin for smooth animations
      // IMPORTANT: Must be last in the plugins array
      "react-native-reanimated/plugin",
    ],
  };
};
