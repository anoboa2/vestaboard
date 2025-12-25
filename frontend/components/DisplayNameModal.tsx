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
import { validateDisplayName, setDisplayName, getDisplayName, clearDisplayName } from "@/lib/display-name";

interface DisplayNameModalProps {
  open: boolean;
  onNameSet: (name: string) => void;
  isEditing?: boolean;
  onClear?: () => void;
  onOpenChange?: (open: boolean) => void;
}

export const DisplayNameModal: React.FC<DisplayNameModalProps> = ({
  open,
  onNameSet,
  isEditing = false,
  onClear,
  onOpenChange,
}) => {
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when modal opens
  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
      // Select all text when editing
      if (isEditing) {
        inputRef.current.select();
      }
    }
  }, [open, isEditing]);

  // Reset state when modal opens - pre-fill if editing
  useEffect(() => {
    if (open) {
      if (isEditing) {
        const currentName = getDisplayName();
        setInputValue(currentName || "");
      } else {
        setInputValue("");
      }
      setError(null);
    }
  }, [open, isEditing]);

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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent 
        className="w-[calc(100vw-2rem)] sm:max-w-md [&>button]:hidden max-h-[90vh] overflow-y-auto"
        onInteractOutside={(e) => {
          // Only prevent closing for initial modal (not editing)
          if (!isEditing) {
            e.preventDefault();
          }
        }}
        onEscapeKeyDown={(e) => {
          // Only prevent closing for initial modal (not editing)
          if (!isEditing) {
            e.preventDefault();
          }
        }}
      >
        <DialogHeader>
          <DialogTitle className="text-lg sm:text-xl">
            {isEditing ? "Edit Display Name" : "Welcome! Enter Your Display Name"}
          </DialogTitle>
          <DialogDescription className="text-sm">
            {isEditing
              ? "Update your display name. This will be shown on your vestaboard messages."
              : "Please enter a display name to continue. This will be shown on your vestaboard messages."}
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
          <div className="flex justify-between gap-2">
            {isEditing && onClear && (
              <Button
                type="button"
                variant="destructive"
                onClick={() => {
                  try {
                    clearDisplayName();
                    if (onClear) {
                      onClear();
                    }
                  } catch (err) {
                    setError(err instanceof Error ? err.message : "Failed to clear display name");
                  }
                }}
                className="w-full sm:w-auto"
              >
                Clear
              </Button>
            )}
            <div className="flex justify-end gap-2 ml-auto">
              <Button type="submit" disabled={isDisabled} className="w-full sm:w-auto">
                {isEditing ? "Save" : "Continue"}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

