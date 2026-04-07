(function setAuraApiBase() {
    const renderApiBase = "https://aura-app-8va5.onrender.com";
    const host = window.location.hostname || "localhost";
    const protocol = window.location.protocol || "";
    const isCapacitorRuntime = protocol === "capacitor:" || protocol === "ionic:" || protocol === "file:";
    const isLocalhost = host === "localhost" || host === "127.0.0.1";
    const localApiBase = `http://${host}:3000`;

    // Capacitor runtime should hit deployed backend by default.
    const defaultApiBase = isCapacitorRuntime ? renderApiBase : (isLocalhost ? localApiBase : renderApiBase);
    window.AURA_API_BASE = window.AURA_API_BASE || defaultApiBase;

    // Supabase configuration
    window.AURA_SUPABASE_URL = window.AURA_SUPABASE_URL || 'https://jbabssesevowywncmtcm.supabase.co';
    window.AURA_SUPABASE_ANON_KEY = window.AURA_SUPABASE_ANON_KEY || 'sb_publishable_84lmX5wogGyMUWEk8q58mg_d4woETVE';

    // RevenueCat configuration — Apple public API key from RevenueCat dashboard
    window.AURA_REVENUECAT_APPLE_KEY = window.AURA_REVENUECAT_APPLE_KEY || 'test_bmrngPaRezJznfNKVRVFxFhBkSP';

    // Apple Sign-In removed — email OTP is the sole auth method.
})();
