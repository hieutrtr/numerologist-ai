import { registerRootComponent } from 'expo';
import { Slot } from 'expo-router';

export default function RootLayout() {
  return <Slot />;
}

registerRootComponent(RootLayout);
