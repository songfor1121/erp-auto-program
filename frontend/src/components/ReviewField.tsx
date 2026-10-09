import { useState } from "react";
import { updateField, FieldData } from "@/lib/api";
import { Check, Edit2, AlertCircle, Loader2 } from "lucide-react";

interface Props {
  docId: number;
  itemIndex?: number;
  label: string;
  fieldName: string;
  data: FieldData;
  onDataUpdated: (newData: any) => void;
}

export default function ReviewField({ docId, itemIndex, label, fieldName, data, onDataUpdated }: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(data.normalized_value || "");
  const [isUpdating, setIsUpdating] = useState(false);

  // Phase 5 ERP_AUTO simulation visually
  const isErpAuto = fieldName === "item_name";

  const handleSave = async () => {
    setIsUpdating(true);
    try {
      const updatedDoc = await updateField(docId, fieldName, editValue, itemIndex);
      onDataUpdated(updatedDoc);
      setIsEditing(false);
    } catch (err) {
      alert("업데이트에 실패했습니다.");
    } finally {
      setIsUpdating(false);
    }
  };

  const statusColor = data.validation_status === "CONFIRMED" ? "text-green-600" : "text-amber-500";
  const bgColor = data.validation_status === "CONFIRMED" ? "bg-green-50" : "bg-amber-50";
  const borderColor = data.validation_status === "CONFIRMED" ? "border-green-200" : "border-amber-200";

  return (
    <div className={`p-3 rounded-md border ${borderColor} ${bgColor} relative group transition-colors`} title={data.validation_message || ""}>
      <div className="flex justify-between items-center mb-1">
        <label className="text-xs font-semibold text-gray-500 uppercase flex items-center">
          {label}
          {isErpAuto && <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-indigo-100 text-indigo-700 rounded-sm">ERP 자동완성</span>}
        </label>
        <div className="flex items-center space-x-1">
          {data.validation_status === "CONFIRMED" ? (
            <Check className={`w-4 h-4 ${statusColor}`} />
          ) : (
            <AlertCircle className={`w-4 h-4 ${statusColor}`} />
          )}
        </div>
      </div>

      {isEditing && !isErpAuto ? (
        <div className="flex space-x-2 mt-1">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm outline-none focus:border-blue-400"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
          />
          <button
            onClick={handleSave}
            disabled={isUpdating}
            className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 disabled:opacity-50 flex items-center"
          >
            {isUpdating ? <Loader2 className="w-3 h-3 animate-spin" /> : "저장"}
          </button>
        </div>
      ) : (
        <div className="flex justify-between items-center mt-1">
          <div className="flex flex-col">
            <span className={`text-base font-medium ${isErpAuto ? 'text-gray-400 italic' : 'text-gray-900'}`}>
              {isErpAuto && !data.normalized_value ? "(ERP 조회 전)" : (data.normalized_value || "-")}
            </span>
            {data.raw_value && data.raw_value !== data.normalized_value && !isErpAuto && (
              <span className="text-xs text-gray-400 line-through mt-0.5">{data.raw_value}</span>
            )}
          </div>
          {!isErpAuto && (
            <button
              onClick={() => setIsEditing(true)}
              className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-white rounded transition-colors opacity-0 group-hover:opacity-100"
              title="수정"
            >
              <Edit2 className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {data.validation_message && !isEditing && (
        <p className={`text-xs mt-1 ${statusColor}`}>
          {data.validation_message}
        </p>
      )}
    </div>
  );
}
