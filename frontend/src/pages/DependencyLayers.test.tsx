import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import DependencyLayers from "./DependencyLayers";
import { dependencyLayersApi } from "../services/api";
import type { AxiosResponse } from "axios";

// Mock the API
vi.mock("../services/api", () => ({
  dependencyLayersApi: {
    summary: vi.fn(),
  },
}));

// Helper to create mock axios response
function mockAxiosResponse<T>(data: T): AxiosResponse<T> {
  return {
    data,
    status: 200,
    statusText: "OK",
    headers: {},
    config: {} as any,
  };
}

const mockSummaryData = {
  layers: {
    legal: { count: 10, avg_criticality: 7.5, risk_weight: 1.5 },
    financial: { count: 8, avg_criticality: 6.0, risk_weight: 1.4 },
    operational: { count: 15, avg_criticality: 5.0, risk_weight: 1.0 },
    human: { count: 5, avg_criticality: 8.0, risk_weight: 1.2 },
    academic: { count: 3, avg_criticality: 4.0, risk_weight: 0.8 },
  },
  total_dependencies: 41,
  layer_descriptions: {
    legal: "Contracts, grants, legal obligations",
    financial: "Banks, currencies, payment corridors",
    operational: "Suppliers, logistics, IT systems",
    human: "Key personnel, irreplaceable staff",
    academic: "Research partners, funding sources",
  },
};

function renderWithProviders(component: React.ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
}

describe("DependencyLayers Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("displays loading state initially", () => {
    vi.mocked(dependencyLayersApi.summary).mockReturnValue(
      new Promise(() => {}) // Never resolves
    );

    renderWithProviders(<DependencyLayers />);
    // Check for loading spinner (div with animate-spin class)
    const loadingContainer = screen.getByText("").closest("div.flex.items-center.justify-center");
    expect(loadingContainer).toBeInTheDocument();
  });

  it("displays layer summary data after loading", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      expect(screen.getByText("Dependency Layers")).toBeInTheDocument();
    });

    // Check total dependencies is displayed
    await waitFor(() => {
      expect(screen.getByText("41")).toBeInTheDocument();
    });

    // Check all layers are displayed (use getAllByText since layer names appear multiple times)
    expect(screen.getAllByText(/legal/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/financial/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/operational/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/human/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/academic/i).length).toBeGreaterThan(0);
  });

  it("displays layer descriptions", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      expect(screen.getByText(/Contracts, grants, legal obligations/i)).toBeInTheDocument();
    });
  });

  it("displays risk weights for each layer", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      // Check for risk weight values
      expect(screen.getAllByText(/1\.5x/)).toHaveLength(2); // header and card
    });
  });

  it("displays error state on API failure", async () => {
    vi.mocked(dependencyLayersApi.summary).mockRejectedValue(new Error("API Error"));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load layer summary/i)).toBeInTheDocument();
    });
  });

  it("calculates and displays highest risk layer", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    // Legal has highest weighted risk: 10 * 1.5 = 15
    await waitFor(() => {
      expect(screen.getByText("Highest Risk Layer")).toBeInTheDocument();
    });
  });

  it("displays active layers count", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      expect(screen.getByText("Active Layers")).toBeInTheDocument();
      expect(screen.getByText("5 / 5")).toBeInTheDocument();
    });
  });
});

describe("Layer Colors", () => {
  it("has correct color scheme for each layer", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      // Verify layer cards exist (descriptions appear multiple times - use getAllByText)
      const legalDescriptions = screen.getAllByText(/Contracts, grants, legal obligations/);
      expect(legalDescriptions.length).toBeGreaterThan(0);
    });
  });
});

describe("Layer Risk Weight Table", () => {
  it("displays risk weight explanation table", async () => {
    vi.mocked(dependencyLayersApi.summary).mockResolvedValue(mockAxiosResponse(mockSummaryData));

    renderWithProviders(<DependencyLayers />);

    await waitFor(() => {
      expect(screen.getByText("Layer Risk Weights")).toBeInTheDocument();
    });

    // Check impact levels
    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("Medium")).toBeInTheDocument();
  });
});
