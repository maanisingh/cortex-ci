import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import CrossLayerAnalysis from "./CrossLayerAnalysis";
import { dependencyLayersApi, entitiesApi } from "../services/api";
import type { AxiosResponse } from "axios";

// Mock the APIs
vi.mock("../services/api", () => ({
  dependencyLayersApi: {
    crossLayerImpact: vi.fn(),
  },
  entitiesApi: {
    list: vi.fn(),
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

const mockEntitiesData = {
  items: [
    { id: "entity-1", name: "Test Bank Corp", type: "ORGANIZATION" },
    { id: "entity-2", name: "Acme Industries", type: "ORGANIZATION" },
    { id: "entity-3", name: "John Doe", type: "INDIVIDUAL" },
  ],
};

const mockCrossLayerImpactData = {
  entity_id: "entity-1",
  entity_name: "Test Bank Corp",
  layer_impact: {
    legal: { outgoing: 3, incoming: 2, risk_score: 15.0 },
    financial: { outgoing: 5, incoming: 4, risk_score: 25.2 },
    operational: { outgoing: 2, incoming: 1, risk_score: 8.0 },
    human: { outgoing: 1, incoming: 0, risk_score: 4.8 },
    academic: { outgoing: 0, incoming: 1, risk_score: 2.4 },
  },
  total_cross_layer_risk: 55.4,
  primary_exposure_layer: "financial",
  total_outgoing: 11,
  total_incoming: 8,
  unique_entities_affected: 15,
  recommendation: "HIGH PRIORITY: Entity has significant cross-layer exposure, primarily in financial. Recommend immediate diversification strategy.",
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

describe("CrossLayerAnalysis Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("displays search input and empty state initially", () => {
    renderWithProviders(<CrossLayerAnalysis />);

    expect(screen.getByText("Cross-Layer Impact Analysis")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search entities by name/i)).toBeInTheDocument();
    expect(screen.getByText("Select an Entity")).toBeInTheDocument();
  });

  it("searches for entities when typing", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      expect(entitiesApi.list).toHaveBeenCalledWith({
        search: "Test",
        page_size: 10,
      });
    });
  });

  it("displays search results as dropdown", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      expect(screen.getByText("Test Bank Corp")).toBeInTheDocument();
    });
  });

  it("loads cross-layer impact after selecting entity", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    // Search and select entity
    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      expect(screen.getByText("Test Bank Corp")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Test Bank Corp"));

    await waitFor(() => {
      expect(dependencyLayersApi.crossLayerImpact).toHaveBeenCalledWith("entity-1");
    });
  });

  it("displays total risk score and risk level", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText("55.4")).toBeInTheDocument();
      expect(screen.getByText("HIGH")).toBeInTheDocument();
    });
  });

  it("displays outgoing and incoming dependency counts", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText("Outgoing Dependencies")).toBeInTheDocument();
      expect(screen.getByText("11")).toBeInTheDocument();
      expect(screen.getByText("Incoming Dependencies")).toBeInTheDocument();
      expect(screen.getByText("8")).toBeInTheDocument();
    });
  });

  it("displays recommendation based on risk", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText(/diversification strategy/i)).toBeInTheDocument();
    });
  });

  it("displays primary exposure layer", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText(/Primary Exposure/i)).toBeInTheDocument();
      // Use getAllByText since "financial" appears multiple times in the UI
      expect(screen.getAllByText(/financial/i).length).toBeGreaterThan(0);
    });
  });

  it("displays layer-by-layer breakdown", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText("Impact by Layer")).toBeInTheDocument();
    });
  });

  it("displays entities affected count", async () => {
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse(mockCrossLayerImpactData)
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });

    await waitFor(() => {
      fireEvent.click(screen.getByText("Test Bank Corp"));
    });

    await waitFor(() => {
      expect(screen.getByText("Entities Affected")).toBeInTheDocument();
      expect(screen.getByText("15")).toBeInTheDocument();
    });
  });
});

describe("Risk Level Classification", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(entitiesApi.list).mockResolvedValue(mockAxiosResponse(mockEntitiesData));
  });

  it("displays HIGH for risk > 50", async () => {
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse({
        ...mockCrossLayerImpactData,
        total_cross_layer_risk: 75.0,
      })
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });
    await waitFor(() => fireEvent.click(screen.getByText("Test Bank Corp")));

    await waitFor(() => {
      expect(screen.getByText("HIGH")).toBeInTheDocument();
    });
  });

  it("displays MEDIUM for risk 25-50", async () => {
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse({
        ...mockCrossLayerImpactData,
        total_cross_layer_risk: 35.0,
      })
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });
    await waitFor(() => fireEvent.click(screen.getByText("Test Bank Corp")));

    await waitFor(() => {
      expect(screen.getByText("MEDIUM")).toBeInTheDocument();
    });
  });

  it("displays LOW for risk 10-25", async () => {
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse({
        ...mockCrossLayerImpactData,
        total_cross_layer_risk: 15.0,
      })
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });
    await waitFor(() => fireEvent.click(screen.getByText("Test Bank Corp")));

    await waitFor(() => {
      expect(screen.getByText("LOW")).toBeInTheDocument();
    });
  });

  it("displays MINIMAL for risk < 10", async () => {
    vi.mocked(dependencyLayersApi.crossLayerImpact).mockResolvedValue(
      mockAxiosResponse({
        ...mockCrossLayerImpactData,
        total_cross_layer_risk: 5.0,
      })
    );

    renderWithProviders(<CrossLayerAnalysis />);

    const searchInput = screen.getByPlaceholderText(/Search entities by name/i);
    fireEvent.change(searchInput, { target: { value: "Test" } });
    await waitFor(() => fireEvent.click(screen.getByText("Test Bank Corp")));

    await waitFor(() => {
      expect(screen.getByText("MINIMAL")).toBeInTheDocument();
    });
  });
});
