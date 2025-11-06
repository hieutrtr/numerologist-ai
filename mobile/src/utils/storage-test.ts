/**
 * Storage Test Utility
 *
 * Use this to verify localStorage is working correctly on web
 * Run in browser console: testWebStorage()
 */

export const testWebStorage = () => {
  const testKey = 'test_storage_key';
  const testValue = 'test_value_' + Date.now();

  console.log('🔍 Testing Web Storage...');

  try {
    // Test localStorage availability
    if (typeof localStorage === 'undefined') {
      console.error('❌ localStorage is not available');
      return false;
    }

    // Test write
    localStorage.setItem(testKey, testValue);
    console.log('✅ Write successful:', testValue);

    // Test read
    const retrieved = localStorage.getItem(testKey);
    if (retrieved === testValue) {
      console.log('✅ Read successful:', retrieved);
    } else {
      console.error('❌ Read failed. Expected:', testValue, 'Got:', retrieved);
      return false;
    }

    // Test remove
    localStorage.removeItem(testKey);
    const afterRemove = localStorage.getItem(testKey);
    if (afterRemove === null) {
      console.log('✅ Remove successful');
    } else {
      console.error('❌ Remove failed. Still exists:', afterRemove);
      return false;
    }

    console.log('✅ All localStorage tests passed!');

    // Check for auth token
    const authToken = localStorage.getItem('auth_token');
    if (authToken) {
      console.log('📦 Found stored auth token (length:', authToken.length, ')');
    } else {
      console.log('📦 No auth token found in storage');
    }

    return true;
  } catch (error) {
    console.error('❌ Storage test failed:', error);
    return false;
  }
};

// Export for browser console
if (typeof window !== 'undefined') {
  (window as any).testWebStorage = testWebStorage;
}