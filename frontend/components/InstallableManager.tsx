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

export const InstallableManager: React.FC = () => {
  const [installables, setInstallables] = useState<Record<string, InstallableInfo>>({});
  const [activeName, setActiveName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchInstallables = useCallback(async () => {
    try {
      setError(null);
      const data: InstallablesResponse = await getInstallables();
      setInstallables(data.installables);
      setActiveName(data.active);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch installables";
      setError(errorMessage);
      console.error("Error fetching installables:", err);
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
        <CardTitle>Installables</CardTitle>
        <CardDescription>
          Manage which installable is active on your Vestaboard
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading && Object.keys(installables).length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">Loading installables...</div>
        ) : error && Object.keys(installables).length === 0 ? (
          <div className="text-center py-4 text-destructive">{error}</div>
        ) : (
          <div className="space-y-4">
            {Object.entries(installables).map(([key, installable]) => {
              const isActive = installable.status === "active";
              return (
                <div
                  key={key}
                  className={`flex items-center justify-between p-4 rounded-lg border ${
                    isActive
                      ? "border-primary bg-primary/5"
                      : "border-border bg-background"
                  }`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{installable.name}</h3>
                      {isActive && (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-primary text-primary-foreground">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {installable.description}
                    </p>
                  </div>
                  <div className="ml-4">
                    {isActive ? (
                      <Button
                        onClick={handleDeactivate}
                        disabled={actionLoading !== null}
                        variant="outline"
                        size="sm"
                      >
                        {actionLoading === "deactivate" ? "Deactivating..." : "Deactivate"}
                      </Button>
                    ) : (
                      <Button
                        onClick={() => handleActivate(key)}
                        disabled={actionLoading !== null}
                        variant="default"
                        size="sm"
                      >
                        {actionLoading === key ? "Activating..." : "Activate"}
                      </Button>
                    )}
                  </div>
                </div>
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

