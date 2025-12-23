"use client";

import React, { useState, useCallback, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  getInstallables,
  getActiveInstallable,
  activateInstallable,
  deactivateInstallable,
  type InstallableInfo,
  type InstallablesResponse,
} from "@/lib/api-client";
import { getDisplayName } from "@/lib/display-name";

export const InstallableManager: React.FC = () => {
  const [installables, setInstallables] = useState<Record<string, InstallableInfo>>({});
  const [activeName, setActiveName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  
  // Check if user is admin (case-insensitive)
  const displayName = getDisplayName();
  const isAdmin = displayName?.toLowerCase() === "alex";

  const fetchInstallables = useCallback(async () => {
    try {
      setError(null);
      const data: InstallablesResponse = await getInstallables();
      setInstallables(data.installables);
      setActiveName(data.active);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch installables";
      // Only set error if it's not a network error (backend offline is expected)
      if (err instanceof TypeError && err.message === 'Failed to fetch') {
        // Backend is offline, silently handle it
        setError(null);
      } else {
        setError(errorMessage);
        // Only log non-network errors
        if (process.env.NODE_ENV === 'development') {
          console.debug("Error fetching installables:", err);
        }
      }
    }
  }, []);

  const handleActivate = useCallback(async (name: string) => {
    setActionLoading(name);
    setError(null);

    try {
      const result = await activateInstallable(name);
      if (result.success) {
        // Refresh the installables to get updated status
        await fetchInstallables();
      } else {
        setError(result.error || "Failed to activate installable");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to activate installable";
      setError(errorMessage);
    } finally {
      setActionLoading(null);
    }
  }, [fetchInstallables]);

  const handleDeactivate = useCallback(async () => {
    setActionLoading("deactivate");
    setError(null);

    try {
      const result = await deactivateInstallable();
      if (result.success) {
        // Refresh the installables to get updated status
        await fetchInstallables();
      } else {
        setError(result.error || result.message || "Failed to deactivate installable");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to deactivate installable";
      setError(errorMessage);
    } finally {
      setActionLoading(null);
    }
  }, [fetchInstallables]);

  // Fetch installables on mount and periodically
  useEffect(() => {
    setLoading(true);
    fetchInstallables().finally(() => setLoading(false));

    // Poll for status updates every 5 seconds
    const interval = setInterval(() => {
      fetchInstallables();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchInstallables]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{isAdmin ? "Installables" : "Apps"}</CardTitle>
            <CardDescription>
              {isAdmin ? "Manage which installable is active on your Vestaboard" : "View available apps"}
            </CardDescription>
          </div>
          {isAdmin && (
            <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-primary/10 text-primary border border-primary/20">
              Admin Mode
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {loading && Object.keys(installables).length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">Loading installables...</div>
        ) : error && Object.keys(installables).length === 0 ? (
          <div className="text-center py-8 text-destructive">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(installables).map(([key, installable]) => {
              const isActive = installable.status === "active" || activeName === key;
              return (
                <Card
                  key={key}
                  className={`transition-all duration-200 hover:shadow-md ${
                    isActive
                      ? "border-primary/50 bg-primary/5 shadow-sm"
                      : "border-border hover:border-primary/20"
                  }`}
                >
                  <div className="flex flex-col h-full p-4 gap-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <h3 className="font-semibold text-base leading-tight">{installable.name}</h3>
                        {isActive && (
                          <div className="flex items-center gap-1.5">
                            <div
                              className="w-2 h-2 rounded-full bg-green-500 animate-pulse flex-shrink-0"
                              title="Active"
                            />
                            {!isAdmin && (
                              <span className="text-xs text-muted-foreground font-medium">Active</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                      {installable.description}
                    </p>
                    {isAdmin && (
                      <div className="mt-auto pt-2">
                        {isActive ? (
                          <Button
                            onClick={handleDeactivate}
                            disabled={actionLoading !== null}
                            variant="outline"
                            size="sm"
                            className="w-full"
                          >
                            {actionLoading === "deactivate" ? "Deactivating..." : "Deactivate"}
                          </Button>
                        ) : (
                          <Button
                            onClick={() => handleActivate(key)}
                            disabled={actionLoading !== null}
                            variant="default"
                            size="sm"
                            className="w-full"
                          >
                            {actionLoading === key ? "Activating..." : "Activate"}
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
        {error && Object.keys(installables).length > 0 && (
          <div className="mt-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

