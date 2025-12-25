"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { validateDisplayName, setDisplayName } from "@/lib/display-name";

interface DisplayNameModalProps {
  open: boolean;
  onNameSet: (name: string) => void;
}

export const DisplayNameModal: React.FC<DisplayNameModalProps> = ({
  open,
  onNameSet,
}) => {
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when modal opens
  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open]);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setInputValue("");
      setError(null);
    }
  }, [open]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const validation = validateDisplayName(inputValue);
    if (!validation.isValid) {
      setError(validation.error || "Invalid display name");
      return;
    }

    try {
      setDisplayName(inputValue);
      onNameSet(inputValue);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save display name");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isDisabled = inputValue.trim().length === 0;

  return (
    <Dialog open={open}>
      <DialogContent 
        className="w-[calc(100vw-2rem)] sm:max-w-md [&>button]:hidden max-h-[90vh] overflow-y-auto"
        onInteractOutside={(e) => e.preventDefault()} // Prevent closing by clicking outside
        onEscapeKeyDown={(e) => e.preventDefault()} // Prevent closing with Escape
      >
        <DialogHeader>
          <DialogTitle className="text-lg sm:text-xl">Welcome! Enter Your Display Name</DialogTitle>
          <DialogDescription className="text-sm">
            Please enter a display name to continue. This will be shown on your vestaboard messages.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Enter your display name"
              className="w-full px-3 py-2.5 sm:py-2 border border-input bg-background rounded-md text-sm sm:text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              maxLength={20}
              autoFocus
            />
            {error && (
              <p className="text-xs sm:text-sm text-red-600 dark:text-red-400">{error}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Up to 20 characters. Allowed: letters, numbers, spaces, hyphens, underscores, and common punctuation.
            </p>
          </div>
          <div className="flex justify-end">
            <Button type="submit" disabled={isDisabled} className="w-full sm:w-auto">
              Continue
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

