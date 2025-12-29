import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";
import Layout from "./components/common/Layout";
import Login from "./pages/Login";
import LandingPage from "./pages/LandingPage";
import TopLanguageBar from "./components/common/TopLanguageBar";
import Dashboard from "./pages/Dashboard";
import Entities from "./pages/Entities";
import EntityDetail from "./pages/EntityDetail";
import Constraints from "./pages/Constraints";
import ConstraintDetail from "./pages/ConstraintDetail";
import Dependencies from "./pages/Dependencies";
import Risks from "./pages/Risks";
import RiskDetail from "./pages/RiskDetail";
import Scenarios from "./pages/Scenarios";
import ScenarioDetail from "./pages/ScenarioDetail";
import AuditLog from "./pages/AuditLog";
import AuditLogDetail from "./pages/AuditLogDetail";
import Settings from "./pages/Settings";
import UserManagement from "./pages/UserManagement";
import Profile from "./pages/Profile";

// Phase 2 pages
import ScenarioChains from "./pages/ScenarioChains";
import RiskJustification from "./pages/RiskJustification";
import History from "./pages/History";
import AIAnalysis from "./pages/AIAnalysis";
import Monitoring from "./pages/Monitoring";
// Phase 2.1 pages
import DependencyLayers from "./pages/DependencyLayers";
import CrossLayerAnalysis from "./pages/CrossLayerAnalysis";
// Phase 3 pages
import SecuritySettings from "./pages/SecuritySettings";
// Phase 4 pages
import BulkOperations from "./pages/BulkOperations";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
// Phase 5 pages
import Simulations from "./pages/Simulations";
// Compliance Platform pages
import ComplianceDashboard from "./pages/ComplianceDashboard";
// GRC Module pages
import Policies from "./pages/Policies";
import Evidence from "./pages/Evidence";
import Audits from "./pages/Audits";
import Findings from "./pages/Findings";
import Incidents from "./pages/Incidents";
import Vendors from "./pages/Vendors";
// Russian Compliance pages
import RussianCompliance from "./pages/RussianCompliance";
import RussianOnboarding from "./pages/RussianOnboarding";
import DocumentEditor from "./pages/DocumentEditor";
import DocumentLibrary from "./pages/DocumentLibrary";
import ComplianceTasks from "./pages/ComplianceTasks";
import RussianDashboard from "./pages/RussianDashboard";
import ComplianceCalendar from "./pages/ComplianceCalendar";
import GapAnalysis from "./pages/GapAnalysis";
import TemplateCatalog from "./pages/TemplateCatalog";
// SME Business Templates pages
import CompanyLifecycle from "./pages/CompanyLifecycle";
import SMETemplates from "./pages/SMETemplates";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top language bar - always visible */}
      <TopLanguageBar />

      <Routes>
        <Route
          path="/"
          element={
            <PublicRoute>
              <LandingPage />
            </PublicRoute>
          }
        />
        <Route path="/welcome" element={<LandingPage />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/entities" element={<Entities />} />
                  <Route path="/entities/:id" element={<EntityDetail />} />
                  <Route path="/constraints" element={<Constraints />} />
                  <Route
                    path="/constraints/:id"
                    element={<ConstraintDetail />}
                  />
                  <Route path="/dependencies" element={<Dependencies />} />
                  <Route path="/risks" element={<Risks />} />
                  <Route path="/risks/:id" element={<RiskDetail />} />
                  <Route path="/scenarios" element={<Scenarios />} />
                  <Route path="/scenarios/:id" element={<ScenarioDetail />} />
                  <Route path="/audit" element={<AuditLog />} />
                  <Route path="/audit/:id" element={<AuditLogDetail />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/admin/users" element={<UserManagement />} />
                  <Route path="/profile" element={<Profile />} />
                  {/* Phase 2 routes */}
                  <Route path="/scenario-chains" element={<ScenarioChains />} />
                  <Route
                    path="/risk-justification"
                    element={<RiskJustification />}
                  />
                  <Route path="/history" element={<History />} />
                  <Route path="/ai-analysis" element={<AIAnalysis />} />
                  <Route path="/monitoring" element={<Monitoring />} />
                  {/* Phase 2.1 routes */}
                  <Route
                    path="/dependency-layers"
                    element={<DependencyLayers />}
                  />
                  <Route
                    path="/cross-layer-analysis"
                    element={<CrossLayerAnalysis />}
                  />
                  {/* Phase 3 routes */}
                  <Route path="/security" element={<SecuritySettings />} />
                  {/* Phase 4 routes */}
                  <Route path="/bulk-operations" element={<BulkOperations />} />
                  <Route path="/analytics" element={<AnalyticsDashboard />} />
                  {/* Phase 5 routes */}
                  <Route path="/simulations" element={<Simulations />} />
                  {/* Compliance Platform routes */}
                  <Route path="/compliance" element={<ComplianceDashboard />} />
                  <Route
                    path="/compliance/dashboard"
                    element={<ComplianceDashboard />}
                  />
                  {/* GRC Module routes */}
                  <Route path="/policies" element={<Policies />} />
                  <Route path="/evidence" element={<Evidence />} />
                  <Route path="/audits" element={<Audits />} />
                  <Route path="/findings" element={<Findings />} />
                  <Route path="/incidents" element={<Incidents />} />
                  <Route path="/vendors" element={<Vendors />} />
                  {/* Russian Compliance routes */}
                  <Route path="/russian-compliance" element={<RussianCompliance />} />
                  <Route path="/russian-onboarding" element={<RussianOnboarding />} />
                  <Route path="/documents" element={<DocumentLibrary />} />
                  <Route path="/documents/:id" element={<DocumentEditor />} />
                  <Route path="/compliance-tasks" element={<ComplianceTasks />} />
                  <Route path="/compliance-calendar" element={<ComplianceCalendar />} />
                  <Route path="/russian-dashboard" element={<RussianDashboard />} />
                  <Route path="/gap-analysis" element={<GapAnalysis />} />
                  <Route path="/templates" element={<TemplateCatalog />} />
                  {/* SME Business Templates routes */}
                  <Route path="/company-lifecycle" element={<CompanyLifecycle />} />
                  <Route path="/sme-templates" element={<SMETemplates />} />
                  {/* Alias routes for navigation */}
                  <Route path="/cross-layer" element={<CrossLayerAnalysis />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;
