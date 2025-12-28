import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { authApi } from "../services/api";
import { useLanguage, LANGUAGES, LanguageCode } from "../contexts/LanguageContext";

export default function Login() {
  const { t, language, setLanguage } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantSlug, setTenantSlug] = useState("default");

  const fillDemoCredentials = () => {
    setEmail("admin@cortex.io");
    setPassword("Admin123!");
    setTenantSlug("default");
  };

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Login and get tokens
      const tokenResponse = await authApi.login(email, password, tenantSlug);
      const tokens = tokenResponse.data;

      // Store tokens first so the interceptor can use them
      useAuthStore.getState().setTokens(tokens);

      // Now get user info (token is available in interceptor)
      const userResponse = await authApi.me();
      const user = userResponse.data;

      // Complete login with user info
      login(user, tokens, user.tenant_id);

      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 to-primary-700 py-12 px-4 sm:px-6 lg:px-8">
      {/* Language selector */}
      <div className="absolute top-4 right-4">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as LanguageCode)}
          className="text-sm border border-white/30 rounded-md px-2 py-1 bg-white/10 text-white backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-white/50"
        >
          {Object.entries(LANGUAGES).map(([code, { nativeName, flag }]) => (
            <option key={code} value={code} className="text-gray-900">
              {flag} {nativeName}
            </option>
          ))}
        </select>
      </div>
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-4xl font-bold text-white">
            CORTEX-CI
          </h1>
          <p className="mt-2 text-center text-primary-200">
            {t("loginSubtitle")}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {t("signInToAccount")}
          </h2>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="tenant"
                className="block text-sm font-medium text-gray-700"
              >
                {t("organization")}
              </label>
              <input
                id="tenant"
                name="tenant"
                type="text"
                value={tenantSlug}
                onChange={(e) => setTenantSlug(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm text-gray-900 bg-white"
                placeholder={t("organizationSlug")}
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                {t("emailAddress")}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm text-gray-900 bg-white"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                {t("password")}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm text-gray-900 bg-white"
                placeholder={t("enterPassword")}
              />
            </div>

            <div className="space-y-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                {loading ? t("signingIn") : t("signIn")}
              </button>

              <button
                type="button"
                onClick={fillDemoCredentials}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                {t("useDemoAccount")}
              </button>
            </div>
          </form>

          <div className="mt-4 p-3 bg-gray-50 rounded-md">
            <p className="text-xs text-gray-500 text-center">
              {t("demoCredentials")}
            </p>
          </div>
        </div>

        <p className="text-center text-primary-200 text-sm">
          {t("governmentGrade")}
        </p>
      </div>
    </div>
  );
}
