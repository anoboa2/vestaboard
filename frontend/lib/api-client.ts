const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Log the API base URL on module load (for debugging)
if (typeof window !== "undefined") {
  console.log(`API Base URL configured: ${API_BASE_URL}`);
}

export interface GridData {
  grid: string[][];
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export interface InstallableInfo {
  name: string;
  description: string;
  status: "active" | "inactive";
}

export interface InstallablesResponse {
  success: boolean;
  installables: Record<string, InstallableInfo>;
  active: string | null;
}

export async function sendGridToBackend(
  grid: string[][]
): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/vestaboard/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ grid }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to send grid to backend",
      }));
      return {
        success: false,
        error: errorData.error || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      message: data.message || "Grid sent successfully",
    };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error ? error.message : "Failed to send grid to backend",
    };
  }
}

export async function getCurrentBoard(): Promise<ApiResponse & { grid?: string[][] }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/vestaboard/current`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to fetch current board",
      }));
      console.error("getCurrentBoard API error:", response.status, errorData);
      return {
        success: false,
        error: errorData.error || errorData.detail || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    console.log("getCurrentBoard API response:", data);
    
    // Always return success with grid, even if it's empty
    return {
      success: true,
      grid: data.grid || [],
      message: data.message || "Board fetched successfully",
    };
  } catch (error) {
    console.error("getCurrentBoard exception:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : "Failed to fetch current board",
    };
  }
}

export async function checkBackendStatus(): Promise<boolean> {
  const url = `${API_BASE_URL}/`;
  console.log(`Checking backend status at: ${url}`);
  
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      // Add mode to handle CORS properly
      mode: "cors",
      // Add cache control to avoid caching issues
      cache: "no-cache",
    });
    
    // Log for debugging
    if (!response.ok) {
      console.warn(`Backend status check failed: ${response.status} ${response.statusText}`);
      return false;
    }
    
    const data = await response.json();
    // Verify we got the expected response
    if (data && data.message === "Vestaboard API") {
      console.log(`Backend is online at ${url}`);
      return true;
    }
    console.warn(`Backend returned unexpected response:`, data);
    return false;
  } catch (error) {
    // Log the actual error for debugging
    console.error(`Backend status check error for ${url}:`, error);
    return false;
  }
}

export async function getInstallables(): Promise<InstallablesResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/installables`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to fetch installables",
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getActiveInstallable(): Promise<{ active: string | null }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/installables/active`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to fetch active installable",
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw error;
  }
}

export async function activateInstallable(name: string): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/installables/${name}/activate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to activate installable",
      }));
      return {
        success: false,
        error: errorData.error || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      message: data.message || "Installable activated successfully",
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to activate installable",
    };
  }
}

export async function deactivateInstallable(): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/installables/deactivate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Failed to deactivate installable",
      }));
      return {
        success: false,
        error: errorData.error || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      message: data.message || "Installable deactivated successfully",
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to deactivate installable",
    };
  }
}

