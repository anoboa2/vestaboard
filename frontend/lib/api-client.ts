const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface GridData {
  grid: string[][];
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
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
      return {
        success: false,
        error: errorData.error || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      grid: data.grid,
      message: data.message || "Board fetched successfully",
    };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : "Failed to fetch current board",
    };
  }
}

