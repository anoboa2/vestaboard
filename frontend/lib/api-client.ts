const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Log the API base URL on module load (for debugging in development only)
if (typeof window !== "undefined" && process.env.NODE_ENV === 'development') {
  console.debug(`API Base URL configured: ${API_BASE_URL}`);
}

export interface GridData {
  grid: string[][];
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  grid?: string[][];  // Backward compatibility
  gridCodes?: number[][];  // Raw character codes for frontend decoding
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
    console.log("Sending grid to backend:", { 
      rows: grid.length, 
      cols: grid[0]?.length,
      url: `${API_BASE_URL}/api/vestaboard/send`
    });
    
    const response = await fetch(`${API_BASE_URL}/api/vestaboard/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ grid }),
    });

    console.log("Response status:", response.status, response.statusText);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
        console.error("Error response data:", errorData);
      } catch (jsonError) {
        const text = await response.text().catch(() => "Failed to read response");
        console.error("Error response text:", text);
        errorData = { detail: text || "Failed to send grid to backend" };
      }
      // FastAPI returns errors in 'detail' field, not 'error'
      const errorMessage = errorData.detail || errorData.error || `HTTP error! status: ${response.status}`;
      console.error("Sending error response:", errorMessage);
      return {
        success: false,
        error: errorMessage,
      };
    }

    try {
      const data = await response.json();
      console.log("Success response data:", data);
      return {
        success: true,
        message: data.message || "Grid sent successfully",
      };
    } catch (jsonError) {
      console.error("Failed to parse success response:", jsonError);
      return {
        success: false,
        error: "Failed to parse response from server",
      };
    }
  } catch (error) {
    console.error("Network/fetch error:", error);
    return {
      success: false,
      error:
        error instanceof Error ? error.message : "Failed to send grid to backend",
    };
  }
}

export async function getCurrentBoard(): Promise<ApiResponse> {
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

    try {
      const data = await response.json();
      if (process.env.NODE_ENV === 'development') {
        console.log("getCurrentBoard API response:", data);
      }
      
      // Always return success with grid, even if it's empty
      return {
        success: true,
        grid: data.grid || [],
        gridCodes: data.gridCodes || undefined, // Include gridCodes if available
        message: data.message || "Board fetched successfully",
      };
    } catch (jsonError) {
      console.error("getCurrentBoard JSON parse error:", jsonError);
      return {
        success: false,
        error: "Failed to parse response from server",
      };
    }
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
  if (process.env.NODE_ENV === 'development') {
    console.debug(`Checking backend status at: ${url}`);
  }
  
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
    
    // Check if response is JSON before parsing
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      console.warn(`Backend returned non-JSON response: ${contentType}`);
      return false;
    }
    
    try {
      const data = await response.json();
      // Verify we got the expected response
      if (data && data.message === "Vestaboard API") {
        if (process.env.NODE_ENV === 'development') {
          console.debug(`Backend is online at ${url}`);
        }
        return true;
      }
      console.warn(`Backend returned unexpected response:`, data);
      return false;
    } catch (jsonError) {
      console.error(`Failed to parse JSON response:`, jsonError);
      return false;
    }
  } catch (error) {
    // Silently handle network errors when backend is offline
    // Only log non-network errors in development
    if (process.env.NODE_ENV === 'development' && error instanceof TypeError && error.message !== 'Failed to fetch') {
      console.debug(`Backend status check error for ${url}:`, error);
    }
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

    try {
      const data = await response.json();
      return data;
    } catch (jsonError) {
      throw new Error("Failed to parse response from server");
    }
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

    try {
      const data = await response.json();
      return data;
    } catch (jsonError) {
      throw new Error("Failed to parse response from server");
    }
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

    try {
      const data = await response.json();
      return {
        success: true,
        message: data.message || "Installable activated successfully",
      };
    } catch (jsonError) {
      return {
        success: false,
        error: "Failed to parse response from server",
      };
    }
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

    try {
      const data = await response.json();
      return {
        success: true,
        message: data.message || "Installable deactivated successfully",
      };
    } catch (jsonError) {
      return {
        success: false,
        error: "Failed to parse response from server",
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Failed to deactivate installable",
    };
  }
}

