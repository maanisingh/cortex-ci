import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "../services/api";
import {
  ShieldCheckIcon,
  KeyIcon,
  DevicePhoneMobileIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon,
  ArrowPathIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/24/outline";

interface MFAStatus {
  mfa_enabled: boolean;
  mfa_verified_at: string | null;
  backup_codes_remaining: number;
}

interface MFASetupData {
  secret: string;
  provisioning_uri: string;
  backup_codes: string[];
}

export default function SecuritySettings() {
  const queryClient = useQueryClient();

  // MFA State
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [mfaSetupData, setMfaSetupData] = useState<MFASetupData | null>(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false);

  // Disable MFA State
  const [showDisableMFA, setShowDisableMFA] = useState(false);
  const [disablePassword, setDisablePassword] = useState("");
  const [disableCode, setDisableCode] = useState("");

  // Password Change State
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPasswords, setShowPasswords] = useState(false);

  // Regenerate Backup Codes State
  const [showRegenerateBackup, setShowRegenerateBackup] = useState(false);
  const [regenerateCode, setRegenerateCode] = useState("");
  const [newBackupCodes, setNewBackupCodes] = useState<string[]>([]);

  // Fetch MFA status
  const { data: mfaStatus, isLoading: mfaLoading } = useQuery<MFAStatus>({
    queryKey: ["mfa-status"],
    queryFn: async () => {
      const response = await authApi.mfa.status();
      return response.data;
    },
  });

  // MFA Setup mutation
  const setupMFAMutation = useMutation({
    mutationFn: async () => {
      const response = await authApi.mfa.setup();
      return response.data;
    },
    onSuccess: (data) => {
      setMfaSetupData(data);
      setShowMFASetup(true);
    },
  });

  // MFA Enable mutation
  const enableMFAMutation = useMutation({
    mutationFn: async (code: string) => {
      const response = await authApi.mfa.enable(code);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mfa-status"] });
      setShowMFASetup(false);
      setMfaSetupData(null);
      setVerificationCode("");
      setShowBackupCodes(false);
    },
  });

  // MFA Disable mutation
  const disableMFAMutation = useMutation({
    mutationFn: async ({
      password,
      code,
    }: {
      password: string;
      code: string;
    }) => {
      const response = await authApi.mfa.disable(password, code);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mfa-status"] });
      setShowDisableMFA(false);
      setDisablePassword("");
      setDisableCode("");
    },
  });

  // Password Change mutation
  const changePasswordMutation = useMutation({
    mutationFn: async (data: {
      current_password: string;
      new_password: string;
    }) => {
      const response = await authApi.changePassword(data);
      return response.data;
    },
    onSuccess: () => {
      setShowPasswordChange(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    },
  });

  // Regenerate Backup Codes mutation
  const regenerateBackupMutation = useMutation({
    mutationFn: async (code: string) => {
      const response = await authApi.mfa.regenerateBackupCodes(code);
      return response.data;
    },
    onSuccess: (data) => {
      setNewBackupCodes(data.backup_codes);
      queryClient.invalidateQueries({ queryKey: ["mfa-status"] });
    },
  });

  const copyBackupCodes = (codes: string[]) => {
    navigator.clipboard.writeText(codes.join("\n"));
    setCopiedBackupCodes(true);
    setTimeout(() => setCopiedBackupCodes(false), 2000);
  };

  const handleEnableMFA = () => {
    if (verificationCode.length === 6) {
      enableMFAMutation.mutate(verificationCode);
    }
  };

  const handleDisableMFA = () => {
    if (disablePassword && disableCode.length === 6) {
      disableMFAMutation.mutate({
        password: disablePassword,
        code: disableCode,
      });
    }
  };

  const handleChangePassword = () => {
    if (newPassword === confirmPassword && newPassword.length >= 8) {
      changePasswordMutation.mutate({
        current_password: currentPassword,
        new_password: newPassword,
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ShieldCheckIcon className="h-7 w-7 text-indigo-600" />
          Security Settings
        </h1>
        <p className="mt-2 text-sm text-gray-700">
          Manage your account security, two-factor authentication, and password
          settings
        </p>
      </div>

      {/* Security Overview Card */}
      <div className="card mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
          <LockClosedIcon className="h-5 w-5 text-indigo-600" />
          Security Overview
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Account Status</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Active
              </span>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Two-Factor Auth</span>
              {mfaLoading ? (
                <span className="text-gray-400">Loading...</span>
              ) : mfaStatus?.mfa_enabled ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Enabled
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                  Disabled
                </span>
              )}
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Backup Codes</span>
              <span className="text-sm font-medium text-gray-900">
                {mfaStatus?.backup_codes_remaining ?? 0} remaining
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Factor Authentication Section */}
      <div className="card mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
          <DevicePhoneMobileIcon className="h-5 w-5 text-indigo-600" />
          Two-Factor Authentication (2FA)
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Add an extra layer of security to your account by requiring a
          verification code from your authenticator app when signing in.
        </p>

        {!mfaStatus?.mfa_enabled ? (
          // MFA Not Enabled - Show Setup
          <div>
            {!showMFASetup ? (
              <button
                onClick={() => setupMFAMutation.mutate()}
                disabled={setupMFAMutation.isPending}
                className="btn btn-primary"
              >
                {setupMFAMutation.isPending ? (
                  <>
                    <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                    Setting up...
                  </>
                ) : (
                  <>
                    <ShieldCheckIcon className="h-4 w-4 mr-2" />
                    Enable Two-Factor Authentication
                  </>
                )}
              </button>
            ) : (
              // MFA Setup Flow
              <div className="border rounded-lg p-6 bg-gray-50">
                <h4 className="font-medium text-gray-900 mb-4">
                  Setup Two-Factor Authentication
                </h4>

                <div className="space-y-6">
                  {/* Step 1: QR Code */}
                  <div>
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-medium">
                        1
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">
                          Scan QR Code
                        </h5>
                        <p className="text-sm text-gray-600 mt-1">
                          Scan this QR code with your authenticator app (Google
                          Authenticator, Authy, etc.)
                        </p>
                        <div className="mt-4 flex items-start gap-6">
                          <div className="bg-white p-4 rounded-lg shadow-sm border">
                            <img
                              src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(mfaSetupData?.provisioning_uri || "")}`}
                              alt="MFA QR Code"
                              className="w-48 h-48"
                            />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm text-gray-500 mb-2">
                              Can't scan? Enter this code manually:
                            </p>
                            <code className="block bg-gray-100 px-3 py-2 rounded text-sm font-mono break-all">
                              {mfaSetupData?.secret}
                            </code>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 2: Backup Codes */}
                  <div>
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-medium">
                        2
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">
                          Save Backup Codes
                        </h5>
                        <p className="text-sm text-gray-600 mt-1">
                          Save these backup codes in a safe place. You can use
                          them to sign in if you lose access to your
                          authenticator.
                        </p>
                        <div className="mt-4">
                          <button
                            onClick={() => setShowBackupCodes(!showBackupCodes)}
                            className="btn btn-secondary text-sm"
                          >
                            {showBackupCodes ? "Hide" : "Show"} Backup Codes
                          </button>
                          {showBackupCodes && mfaSetupData?.backup_codes && (
                            <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                              <div className="flex items-center justify-between mb-3">
                                <span className="text-sm font-medium text-yellow-800">
                                  Your Backup Codes
                                </span>
                                <button
                                  onClick={() =>
                                    copyBackupCodes(mfaSetupData.backup_codes)
                                  }
                                  className="text-sm text-yellow-700 hover:text-yellow-900 flex items-center gap-1"
                                >
                                  <ClipboardDocumentIcon className="h-4 w-4" />
                                  {copiedBackupCodes ? "Copied!" : "Copy All"}
                                </button>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                {mfaSetupData.backup_codes.map((code, idx) => (
                                  <code
                                    key={idx}
                                    className="bg-white px-3 py-1.5 rounded text-sm font-mono text-center border"
                                  >
                                    {code}
                                  </code>
                                ))}
                              </div>
                              <p className="mt-3 text-xs text-yellow-700">
                                Each code can only be used once. Store them
                                securely!
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 3: Verify */}
                  <div>
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-medium">
                        3
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">
                          Verify Setup
                        </h5>
                        <p className="text-sm text-gray-600 mt-1">
                          Enter the 6-digit code from your authenticator app to
                          complete setup.
                        </p>
                        <div className="mt-4 flex items-center gap-4">
                          <input
                            type="text"
                            value={verificationCode}
                            onChange={(e) =>
                              setVerificationCode(
                                e.target.value.replace(/\D/g, "").slice(0, 6),
                              )
                            }
                            placeholder="000000"
                            className="input w-32 text-center text-lg font-mono tracking-widest"
                            maxLength={6}
                          />
                          <button
                            onClick={handleEnableMFA}
                            disabled={
                              verificationCode.length !== 6 ||
                              enableMFAMutation.isPending
                            }
                            className="btn btn-primary"
                          >
                            {enableMFAMutation.isPending
                              ? "Verifying..."
                              : "Enable 2FA"}
                          </button>
                          <button
                            onClick={() => {
                              setShowMFASetup(false);
                              setMfaSetupData(null);
                              setVerificationCode("");
                            }}
                            className="btn btn-secondary"
                          >
                            Cancel
                          </button>
                        </div>
                        {enableMFAMutation.isError && (
                          <p className="mt-2 text-sm text-red-600">
                            Invalid verification code. Please try again.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          // MFA Enabled - Show Status and Disable Option
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">
                    Two-Factor Authentication is Enabled
                  </p>
                  <p className="text-sm text-green-700">
                    Enabled on{" "}
                    {mfaStatus.mfa_verified_at
                      ? new Date(mfaStatus.mfa_verified_at).toLocaleDateString()
                      : "N/A"}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setShowRegenerateBackup(true)}
                className="btn btn-secondary"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Regenerate Backup Codes
              </button>
              <button
                onClick={() => setShowDisableMFA(true)}
                className="btn btn-danger"
              >
                Disable 2FA
              </button>
            </div>

            {/* Disable MFA Modal */}
            {showDisableMFA && (
              <div className="border border-red-200 bg-red-50 rounded-lg p-4 mt-4">
                <h4 className="font-medium text-red-900 mb-3">
                  Disable Two-Factor Authentication
                </h4>
                <p className="text-sm text-red-700 mb-4">
                  This will remove the extra security layer from your account.
                  Are you sure?
                </p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Password
                    </label>
                    <input
                      type="password"
                      value={disablePassword}
                      onChange={(e) => setDisablePassword(e.target.value)}
                      className="input mt-1"
                      placeholder="Enter your password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Authenticator Code
                    </label>
                    <input
                      type="text"
                      value={disableCode}
                      onChange={(e) =>
                        setDisableCode(
                          e.target.value.replace(/\D/g, "").slice(0, 6),
                        )
                      }
                      className="input mt-1 w-32 text-center font-mono"
                      placeholder="000000"
                      maxLength={6}
                    />
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleDisableMFA}
                      disabled={
                        !disablePassword ||
                        disableCode.length !== 6 ||
                        disableMFAMutation.isPending
                      }
                      className="btn btn-danger"
                    >
                      {disableMFAMutation.isPending
                        ? "Disabling..."
                        : "Confirm Disable"}
                    </button>
                    <button
                      onClick={() => {
                        setShowDisableMFA(false);
                        setDisablePassword("");
                        setDisableCode("");
                      }}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Regenerate Backup Codes Modal */}
            {showRegenerateBackup && (
              <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-4 mt-4">
                <h4 className="font-medium text-yellow-900 mb-3">
                  Regenerate Backup Codes
                </h4>
                <p className="text-sm text-yellow-700 mb-4">
                  This will invalidate all existing backup codes. Enter your
                  current 2FA code to continue.
                </p>
                {newBackupCodes.length === 0 ? (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Authenticator Code
                      </label>
                      <input
                        type="text"
                        value={regenerateCode}
                        onChange={(e) =>
                          setRegenerateCode(
                            e.target.value.replace(/\D/g, "").slice(0, 6),
                          )
                        }
                        className="input mt-1 w-32 text-center font-mono"
                        placeholder="000000"
                        maxLength={6}
                      />
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() =>
                          regenerateBackupMutation.mutate(regenerateCode)
                        }
                        disabled={
                          regenerateCode.length !== 6 ||
                          regenerateBackupMutation.isPending
                        }
                        className="btn btn-primary"
                      >
                        {regenerateBackupMutation.isPending
                          ? "Generating..."
                          : "Generate New Codes"}
                      </button>
                      <button
                        onClick={() => {
                          setShowRegenerateBackup(false);
                          setRegenerateCode("");
                        }}
                        className="btn btn-secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="bg-white border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-900">
                          New Backup Codes
                        </span>
                        <button
                          onClick={() => copyBackupCodes(newBackupCodes)}
                          className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                        >
                          <ClipboardDocumentIcon className="h-4 w-4" />
                          {copiedBackupCodes ? "Copied!" : "Copy All"}
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        {newBackupCodes.map((code, idx) => (
                          <code
                            key={idx}
                            className="bg-gray-100 px-3 py-1.5 rounded text-sm font-mono text-center"
                          >
                            {code}
                          </code>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setShowRegenerateBackup(false);
                        setRegenerateCode("");
                        setNewBackupCodes([]);
                      }}
                      className="btn btn-secondary mt-4"
                    >
                      Done
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Password Section */}
      <div className="card mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
          <KeyIcon className="h-5 w-5 text-indigo-600" />
          Password
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Change your password regularly to keep your account secure. Use a
          strong, unique password.
        </p>

        {!showPasswordChange ? (
          <button
            onClick={() => setShowPasswordChange(true)}
            className="btn btn-secondary"
          >
            Change Password
          </button>
        ) : (
          <div className="border rounded-lg p-4 bg-gray-50">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <div className="relative mt-1">
                  <input
                    type={showPasswords ? "text" : "password"}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="input pr-10"
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords(!showPasswords)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPasswords ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <input
                  type={showPasswords ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="input mt-1"
                  placeholder="Enter new password (min. 8 characters)"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <input
                  type={showPasswords ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input mt-1"
                  placeholder="Confirm new password"
                />
                {confirmPassword && newPassword !== confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">
                    Passwords do not match
                  </p>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleChangePassword}
                  disabled={
                    !currentPassword ||
                    newPassword.length < 8 ||
                    newPassword !== confirmPassword ||
                    changePasswordMutation.isPending
                  }
                  className="btn btn-primary"
                >
                  {changePasswordMutation.isPending
                    ? "Changing..."
                    : "Change Password"}
                </button>
                <button
                  onClick={() => {
                    setShowPasswordChange(false);
                    setCurrentPassword("");
                    setNewPassword("");
                    setConfirmPassword("");
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
              {changePasswordMutation.isError && (
                <p className="text-sm text-red-600">
                  Failed to change password. Please check your current password.
                </p>
              )}
              {changePasswordMutation.isSuccess && (
                <p className="text-sm text-green-600">
                  Password changed successfully!
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Security Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-medium text-blue-900 mb-4">
          Security Tips
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start gap-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>
              Enable two-factor authentication for enhanced account security
            </span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>
              Use a unique, strong password with at least 12 characters
            </span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>
              Store your backup codes in a secure location (e.g., password
              manager)
            </span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>Never share your password or backup codes with anyone</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>Log out from shared or public computers after use</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
