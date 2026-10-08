"use client";
import { useState } from "react";
import { FieldData, updateField } from "@/lib/api";

interface Props {
  docId: number;
  label: string;
  fieldName: string;
  data: FieldData;
  itemIndex?: number;
}

interface ExtendedProps extends Props {
  onDataUpdated: (newData: unknown) => void;
}

export default function ReviewField({ docId, label, fieldName, data, itemIndex, onDataUpdated }: ExtendedProps) {
  const [value, setValue] = useState(data.normalized_value || "");

  // Depend directly on props so updates flow top-down when API refreshes
  const isNeedsReview = data.validation_status === "NEEDS_REVIEW";

  const handleBlur = async () => {
    // Only update if value actually changed
    if (value !== data.normalized_value) {
      try {
        const newData = await updateField(docId, fieldName, value, itemIndex);
        if (onDataUpdated) {
          onDataUpdated(newData);
        }
      } catch (err) {
        console.error("Failed to update field", err);
      }
    }
  };

  return (
    <div className="flex flex-col mb-4">
      <label className="text-sm font-semibold text-gray-700 mb-1">{label}</label>
      <div className="relative flex items-center">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={handleBlur}
          className={`w-full p-2 border rounded focus:outline-none focus:ring-2 ${
            isNeedsReview ? "border-red-400 bg-red-50 focus:ring-red-400" : "border-gray-300 focus:ring-blue-500"
          }`}
          data-testid={`input-${fieldName}${itemIndex !== undefined ? `-${itemIndex}` : ''}`}
        />
        {isNeedsReview ? (
          <span className="ml-2 text-sm text-red-600 whitespace-nowrap font-medium flex items-center">
            <span className="mr-1">⚠</span> 확인 필요
          </span>
        ) : (
          <span className="ml-2 text-sm text-green-600 whitespace-nowrap font-medium flex items-center">
            ✓
          </span>
        )}
      </div>
      <div className="text-xs text-gray-400 mt-1 flex justify-between">
        <span>원문: {data.raw_value || "없음"} ({( (data.confidence || 0) * 100).toFixed(0)}%)</span>
        {isNeedsReview && data.validation_message && (
          <span className="text-red-500 font-semibold">{data.validation_message}</span>
        )}
      </div>
    </div>
  );
}
