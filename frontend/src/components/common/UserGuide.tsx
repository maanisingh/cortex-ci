import { useState, useEffect } from "react";
import {
  QuestionMarkCircleIcon,
  XMarkIcon,
  BookOpenIcon,
  PlayIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  CubeTransparentIcon,
  ChartBarIcon,
  ArrowPathIcon,
  BoltIcon,
  MapIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowRightIcon,
} from "@heroicons/react/24/outline";

interface GuideSection {
  id: string;
  title: string;
  icon: React.ElementType;
  content: string;
  steps?: string[];
  tips?: string[];
}

interface TourStep {
  target: string;
  title: string;
  content: string;
  position: "top" | "bottom" | "left" | "right";
}

const GUIDE_SECTIONS: GuideSection[] = [
  {
    id: "overview",
    title: "Platform Overview",
    icon: BookOpenIcon,
    content: `CORTEX-CI is a Government-grade Constraint Intelligence Platform designed for comprehensive compliance monitoring, risk management, and scenario simulation. The platform enables organizations to:

• Monitor sanctions and regulatory constraints in real-time
• Map complex dependency relationships across your organization
• Simulate what-if scenarios for risk assessment
• Track and audit all compliance decisions
• Generate actionable insights from constraint data`,
    tips: [
      "Use the dashboard as your central command center for quick insights",
      "Set up real-time alerts for critical constraint changes",
      "Regularly run scenario simulations to prepare for potential risks",
    ],
  },
  {
    id: "entities",
    title: "Entity Management",
    icon: CubeTransparentIcon,
    content: `Entities represent the core subjects being monitored - individuals, organizations, vessels, or any trackable subject. Each entity has:

• **Name & Type**: Basic identification
• **Risk Score**: Calculated based on constraints and dependencies
• **Constraints**: Active regulations affecting this entity
• **Dependencies**: Relationships with other entities
• **Metadata**: Custom attributes for flexible tracking`,
    steps: [
      "Navigate to Entities from the sidebar",
      "Click 'Add Entity' to create a new entity",
      "Fill in the required fields (name, type)",
      "Add relevant metadata as key-value pairs",
      "Save and view the entity's risk profile",
    ],
    tips: [
      "Use entity types to categorize and filter efficiently",
      "Keep metadata consistent across similar entities",
      "Review high-risk entities weekly",
    ],
  },
  {
    id: "constraints",
    title: "Constraint Monitoring",
    icon: ShieldCheckIcon,
    content: `Constraints are the regulatory and compliance rules that affect your entities. CORTEX-CI supports multiple constraint types:

• **Regulations**: Government laws and regulatory requirements
• **Compliance**: Internal compliance policies
• **Contractual**: Third-party contract obligations
• **Security**: Security requirements and clearances
• **Operational**: Business operational constraints
• **Policy**: Internal policy requirements`,
    steps: [
      "Go to Constraints section",
      "View active constraints by type and severity",
      "Click on a constraint to see affected entities",
      "Set up alerts for constraint expirations",
      "Track constraint history and changes",
    ],
    tips: [
      "Critical constraints should have automated alerts",
      "Review expiring constraints 30 days in advance",
      "Link constraints to specific entities for accurate risk scoring",
    ],
  },
  {
    id: "dependencies",
    title: "Dependency Mapping",
    icon: MapIcon,
    content: `The dependency graph visualizes relationships between entities across multiple layers:

• **Legal Layer**: Contracts, grants, legal obligations
• **Financial Layer**: Banking relationships, payment corridors
• **Operational Layer**: Suppliers, logistics, IT systems
• **Human Layer**: Key personnel, critical roles
• **Academic Layer**: Research partners, institutional affiliations

Understanding these dependencies helps identify cascading risks and hidden exposures.`,
    steps: [
      "Access Dependencies from the navigation",
      "Use the visual graph to explore relationships",
      "Filter by layer to focus on specific dependency types",
      "Click on edges to see dependency details",
      "Identify critical paths and single points of failure",
    ],
    tips: [
      "Start by mapping your most critical dependencies",
      "Use cross-layer analysis to find hidden risks",
      "Review dependency changes when entities change status",
    ],
  },
  {
    id: "scenarios",
    title: "Scenario Simulation",
    icon: BoltIcon,
    content: `What-if analysis allows you to simulate potential changes before they happen:

• **Constraint Changes**: What if a new sanction is applied?
• **Entity Status Changes**: What if a vendor is sanctioned?
• **Dependency Failures**: What if a critical supplier fails?
• **Cascading Effects**: What are the second-order impacts?

Simulations help you prepare contingency plans and understand risk exposure.`,
    steps: [
      "Navigate to Scenarios section",
      "Click 'New Scenario' to create a simulation",
      "Define the hypothetical change (add/remove constraint)",
      "Select affected entities",
      "Run the simulation to see impacts",
      "Review cascading effects across dependencies",
      "Save scenario for future reference",
    ],
    tips: [
      "Run quarterly scenario exercises for critical risks",
      "Create scenario chains for complex multi-step events",
      "Document findings and mitigation strategies",
    ],
  },
  {
    id: "risks",
    title: "Risk Assessment",
    icon: ExclamationTriangleIcon,
    content: `Risk scores are calculated based on multiple factors:

• **Constraint Severity**: Critical, High, Medium, Low
• **Constraint Count**: Number of active constraints
• **Dependency Exposure**: Risk from connected entities
• **Historical Patterns**: Past risk trends

The Risk Justification Engine explains why each score was assigned, providing transparency for audits.`,
    steps: [
      "View overall risk distribution on Dashboard",
      "Access Risks page for detailed breakdown",
      "Click on high-risk entities to see justification",
      "Review risk trends over time",
      "Export risk reports for stakeholders",
    ],
    tips: [
      "Focus on risk trends, not just current scores",
      "Use risk justification for audit documentation",
      "Set thresholds for automatic escalation",
    ],
  },
  {
    id: "analytics",
    title: "Analytics & Reporting",
    icon: ChartBarIcon,
    content: `CORTEX-CI provides comprehensive analytics capabilities:

• **Dashboard Metrics**: Real-time overview of key metrics
• **Risk Trends**: Historical risk score analysis
• **Constraint Analytics**: Constraint distribution and expiration tracking
• **Dependency Analysis**: Network analysis and critical path identification
• **Audit Reports**: Compliance and decision audit trails

All data can be exported for external reporting and integration.`,
    steps: [
      "Use Dashboard for executive summary",
      "Access Analytics Dashboard for detailed metrics",
      "Set up custom date ranges for trend analysis",
      "Export reports in various formats",
      "Schedule automated reports",
    ],
  },
  {
    id: "security",
    title: "Security & Access",
    icon: ShieldCheckIcon,
    content: `CORTEX-CI implements enterprise-grade security:

• **Role-Based Access**: Admin, Analyst, Viewer roles
• **Audit Logging**: Complete activity trail
• **Session Management**: Secure session handling
• **API Security**: Token-based authentication
• **Data Encryption**: Encrypted at rest and in transit`,
    steps: [
      "Review user access in User Management",
      "Check Audit Log for recent activities",
      "Configure Security Settings as needed",
      "Set up multi-factor authentication (if available)",
      "Review and rotate API keys periodically",
    ],
  },
];

const TOUR_STEPS: TourStep[] = [
  {
    target: "[data-tour='dashboard']",
    title: "Welcome to CORTEX-CI",
    content:
      "This is your executive dashboard showing key metrics and risk overview.",
    position: "bottom",
  },
  {
    target: "[data-tour='entities']",
    title: "Entity Management",
    content:
      "Manage all monitored entities including individuals, organizations, and assets.",
    position: "right",
  },
  {
    target: "[data-tour='constraints']",
    title: "Constraint Monitoring",
    content: "View and manage all regulatory and compliance constraints.",
    position: "right",
  },
  {
    target: "[data-tour='scenarios']",
    title: "Scenario Simulation",
    content:
      "Run what-if analyses to understand potential impacts before they happen.",
    position: "right",
  },
  {
    target: "[data-tour='risks']",
    title: "Risk Assessment",
    content: "View risk scores and justifications for all monitored entities.",
    position: "right",
  },
];

export default function UserGuide() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string | null>("overview");
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["overview"]),
  );
  const [showTour, setShowTour] = useState(false);
  const [tourStep, setTourStep] = useState(0);
  const [hasSeenTour, setHasSeenTour] = useState(() => {
    return localStorage.getItem("cortex_tour_completed") === "true";
  });

  useEffect(() => {
    // Show tour for first-time users
    if (!hasSeenTour && !localStorage.getItem("cortex_tour_dismissed")) {
      const timer = setTimeout(() => {
        setShowTour(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [hasSeenTour]);

  const toggleSection = (id: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedSections(newExpanded);
    setActiveSection(id);
  };

  const startTour = () => {
    setIsOpen(false);
    setShowTour(true);
    setTourStep(0);
  };

  const nextTourStep = () => {
    if (tourStep < TOUR_STEPS.length - 1) {
      setTourStep(tourStep + 1);
    } else {
      completeTour();
    }
  };

  const completeTour = () => {
    setShowTour(false);
    setHasSeenTour(true);
    localStorage.setItem("cortex_tour_completed", "true");
  };

  const dismissTour = () => {
    setShowTour(false);
    localStorage.setItem("cortex_tour_dismissed", "true");
  };

  const renderContent = (content: string) => {
    return content.split("\n").map((line, i) => {
      if (line.startsWith("•")) {
        const boldMatch = line.match(/\*\*(.*?)\*\*/);
        if (boldMatch) {
          const parts = line.split(/\*\*.*?\*\*/);
          return (
            <p key={i} className="ml-4 text-sm text-gray-600">
              {parts[0]}
              <strong className="text-gray-900">{boldMatch[1]}</strong>
              {parts[1]}
            </p>
          );
        }
        return (
          <p key={i} className="ml-4 text-sm text-gray-600">
            {line}
          </p>
        );
      }
      return (
        <p key={i} className="text-sm text-gray-600 mb-2">
          {line}
        </p>
      );
    });
  };

  return (
    <>
      {/* Help Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-indigo-600 text-white p-3 rounded-full shadow-lg hover:bg-indigo-700 transition-colors z-40 group"
        title="Help & User Guide"
      >
        <QuestionMarkCircleIcon className="h-6 w-6" />
        <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm px-3 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
          Help & User Guide
        </span>
      </button>

      {/* Guide Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute inset-y-0 right-0 max-w-2xl w-full bg-white shadow-xl flex flex-col">
            {/* Header */}
            <div className="px-6 py-4 border-b flex items-center justify-between bg-indigo-600 text-white">
              <div className="flex items-center gap-3">
                <BookOpenIcon className="h-6 w-6" />
                <h2 className="text-xl font-semibold">CORTEX-CI User Guide</h2>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-indigo-700 p-2 rounded"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Tour Button */}
            <div className="px-6 py-3 bg-indigo-50 border-b flex items-center justify-between">
              <div className="flex items-center gap-2 text-indigo-700">
                <PlayIcon className="h-5 w-5" />
                <span className="text-sm font-medium">New to CORTEX-CI?</span>
              </div>
              <button
                onClick={startTour}
                className="bg-indigo-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-indigo-700 flex items-center gap-1"
              >
                Start Guided Tour
                <ArrowRightIcon className="h-4 w-4" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6">
                {/* Quick Links */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">
                    Quick Navigation
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {GUIDE_SECTIONS.slice(0, 6).map((section) => (
                      <button
                        key={section.id}
                        onClick={() => {
                          setActiveSection(section.id);
                          setExpandedSections(new Set([section.id]));
                        }}
                        className={`flex items-center gap-2 p-2 rounded text-sm text-left ${
                          activeSection === section.id
                            ? "bg-indigo-100 text-indigo-700"
                            : "hover:bg-gray-100 text-gray-700"
                        }`}
                      >
                        <section.icon className="h-4 w-4 flex-shrink-0" />
                        {section.title}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Sections */}
                <div className="space-y-2">
                  {GUIDE_SECTIONS.map((section) => (
                    <div
                      key={section.id}
                      className="border rounded-lg overflow-hidden"
                    >
                      <button
                        onClick={() => toggleSection(section.id)}
                        className={`w-full flex items-center justify-between p-4 text-left ${
                          expandedSections.has(section.id)
                            ? "bg-indigo-50"
                            : "hover:bg-gray-50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <section.icon
                            className={`h-5 w-5 ${
                              expandedSections.has(section.id)
                                ? "text-indigo-600"
                                : "text-gray-500"
                            }`}
                          />
                          <span
                            className={`font-medium ${
                              expandedSections.has(section.id)
                                ? "text-indigo-900"
                                : "text-gray-900"
                            }`}
                          >
                            {section.title}
                          </span>
                        </div>
                        {expandedSections.has(section.id) ? (
                          <ChevronDownIcon className="h-5 w-5 text-indigo-600" />
                        ) : (
                          <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                        )}
                      </button>

                      {expandedSections.has(section.id) && (
                        <div className="p-4 pt-0 border-t bg-white">
                          <div className="prose prose-sm max-w-none">
                            {renderContent(section.content)}
                          </div>

                          {section.steps && (
                            <div className="mt-4 bg-blue-50 rounded-lg p-4">
                              <h4 className="flex items-center gap-2 text-sm font-semibold text-blue-900 mb-2">
                                <ArrowPathIcon className="h-4 w-4" />
                                Step-by-Step Guide
                              </h4>
                              <ol className="list-decimal list-inside space-y-1">
                                {section.steps.map((step, i) => (
                                  <li key={i} className="text-sm text-blue-800">
                                    {step}
                                  </li>
                                ))}
                              </ol>
                            </div>
                          )}

                          {section.tips && (
                            <div className="mt-4 bg-amber-50 rounded-lg p-4">
                              <h4 className="flex items-center gap-2 text-sm font-semibold text-amber-900 mb-2">
                                <LightBulbIcon className="h-4 w-4" />
                                Pro Tips
                              </h4>
                              <ul className="space-y-1">
                                {section.tips.map((tip, i) => (
                                  <li
                                    key={i}
                                    className="flex items-start gap-2 text-sm text-amber-800"
                                  >
                                    <CheckCircleIcon className="h-4 w-4 flex-shrink-0 mt-0.5" />
                                    {tip}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t bg-gray-50 text-center text-xs text-gray-500">
              CORTEX-CI v1.0.0 • Government-grade Constraint Intelligence
              Platform
            </div>
          </div>
        </div>
      )}

      {/* Guided Tour Overlay */}
      {showTour && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black bg-opacity-60" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                <PlayIcon className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">
                  {TOUR_STEPS[tourStep].title}
                </h3>
                <p className="text-sm text-gray-500">
                  Step {tourStep + 1} of {TOUR_STEPS.length}
                </p>
              </div>
            </div>
            <p className="text-gray-600 mb-6">{TOUR_STEPS[tourStep].content}</p>
            <div className="flex justify-between items-center">
              <button
                onClick={dismissTour}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip Tour
              </button>
              <div className="flex gap-2">
                {tourStep > 0 && (
                  <button
                    onClick={() => setTourStep(tourStep - 1)}
                    className="px-4 py-2 text-sm border rounded hover:bg-gray-50"
                  >
                    Back
                  </button>
                )}
                <button
                  onClick={nextTourStep}
                  className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-1"
                >
                  {tourStep === TOUR_STEPS.length - 1 ? "Finish" : "Next"}
                  <ChevronRightIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
            {/* Progress dots */}
            <div className="flex justify-center gap-1 mt-4">
              {TOUR_STEPS.map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i === tourStep ? "bg-indigo-600" : "bg-gray-300"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
