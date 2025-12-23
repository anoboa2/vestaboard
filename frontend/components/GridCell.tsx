"use client";

import React, { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

interface GridCellProps {
  value: string;
  color?: string | null;
  isFocused: boolean;
  row: number;
  col: number;
  onFocus: () => void;
  onChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  onClick?: () => void;
  disabled?: boolean;
}

// Color mapping for Vestaboard colors - apply to the character itself
const COLOR_TEXT_CLASSES: Record<string, string> = {
  red: "text-red-600",
  orange: "text-orange-500",
  yellow: "text-yellow-500",
  green: "text-green-600",
  blue: "text-blue-600",
  purple: "text-purple-600",
  white: "text-gray-200",
  black: "text-black",
  filled: "text-gray-900",
};

export const GridCell: React.FC<GridCellProps> = ({
  value,
  color,
  isFocused,
  row,
  col,
  onFocus,
  onChange,
  onKeyDown,
  onClick,
  disabled = false,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isFocused && inputRef.current && !disabled) {
      inputRef.current.focus();
      // Select all text when focusing so typing replaces the existing value
      inputRef.current.select();
    }
  }, [isFocused, disabled]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    const newValue = e.target.value;
    // Always take the last character typed (handles both new input and editing existing cells)
    // If user is editing, the input will have old char + new char, so we take the last one
    // If user is clearing, newValue will be empty, so we pass empty string
    if (newValue.length === 0) {
      onChange("");
    } else {
      // Take the last character to handle both new input and replacement
      onChange(newValue.slice(-1));
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    e.preventDefault();
    const pastedText = e.clipboardData.getData("text");
    if (pastedText.length > 0) {
      onChange(pastedText[0]);
    }
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    if (disabled) {
      // Prevent focus entirely on disabled cells
      e.target.blur();
      return;
    }
    onFocus();
  };

  const handleClick = (e: React.MouseEvent<HTMLInputElement>) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    // If onClick is provided, call it (for paint mode)
    // Otherwise, default behavior (focus for text mode)
    if (onClick) {
      e.preventDefault();
      onClick();
    }
  };

  // Get text color class if color is set - this colors the character itself
  const textColorClass = color ? COLOR_TEXT_CLASSES[color.toLowerCase()] || "" : "";

  // For disabled cells, use a div instead of input to prevent any interaction
  if (disabled) {
    return (
      <div
        className={cn(
          "w-full h-full text-center text-lg font-mono border rounded transition-all duration-200",
          "bg-gray-100 dark:bg-gray-900/50 border-gray-100 dark:border-gray-800/50",
          "flex items-center justify-center",
          // Apply text color to the character if color is set
          textColorClass,
          // Make block character bold and larger for better visibility
          color && value === "█" ? "font-bold text-2xl" : ""
        )}
        data-row={row}
        data-col={col}
        data-color={color || ""}
        aria-label={`Cell at row ${row + 1}, column ${col + 1}${color ? `, color: ${color}` : ""}, read-only`}
      >
        {value}
      </div>
    );
  }

  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={handleChange}
      onPaste={handlePaste}
      onFocus={handleFocus}
      onClick={handleClick}
      onKeyDown={onKeyDown}
      className={cn(
        "w-full h-full text-center text-lg font-mono border-2 rounded transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1",
        "bg-background",
        isFocused
          ? "border-primary scale-105 shadow-md z-10"
          : "border-border hover:border-primary/50",
        "focus:border-primary",
        // Apply text color to the character if color is set
        textColorClass,
        // Make block character bold and larger for better visibility
        color && value === "█" ? "font-bold text-2xl" : ""
      )}
      maxLength={1}
      aria-label={`Cell at row ${row + 1}, column ${col + 1}${color ? `, color: ${color}` : ""}`}
      data-row={row}
      data-col={col}
      data-color={color || ""}
    />
  );
};

