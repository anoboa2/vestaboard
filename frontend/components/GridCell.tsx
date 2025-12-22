"use client";

import React, { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

interface GridCellProps {
  value: string;
  isFocused: boolean;
  row: number;
  col: number;
  onFocus: () => void;
  onChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

export const GridCell: React.FC<GridCellProps> = ({
  value,
  isFocused,
  row,
  col,
  onFocus,
  onChange,
  onKeyDown,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isFocused && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isFocused]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    // Only allow single character
    if (newValue.length <= 1) {
      onChange(newValue.slice(-1));
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData("text");
    if (pastedText.length > 0) {
      onChange(pastedText[0]);
    }
  };

  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={handleChange}
      onPaste={handlePaste}
      onFocus={onFocus}
      onKeyDown={onKeyDown}
      className={cn(
        "w-full h-full text-center text-lg font-mono bg-background border-2 rounded transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1",
        isFocused
          ? "border-primary scale-105 shadow-md z-10"
          : "border-border hover:border-primary/50",
        "focus:border-primary"
      )}
      maxLength={1}
      aria-label={`Cell at row ${row + 1}, column ${col + 1}`}
      data-row={row}
      data-col={col}
    />
  );
};

