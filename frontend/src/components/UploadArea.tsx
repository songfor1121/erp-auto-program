"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, Loader2 } from "lucide-react";
import { uploadDocument } from "@/lib/api";

export default function UploadArea() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = useCallback(async (file: File) => {
    setIsLoading(true);
    try {
      const data = await uploadDocument(file);
      router.push(`/review/${data.document_id}`);
    } catch (err: unknown) {
      console.error(err);
      alert("업로드에 실패했습니다. (이미지나 PDF를 선택해주세요)");
      setIsLoading(false);
    }
  }, [router]);

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  }, [handleUpload]);

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg bg-gray-50 border-gray-300">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
        <p className="text-gray-600 font-medium">거래명세서를 분석하고 있습니다...</p>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
      className={`relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg transition-colors cursor-pointer ${
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-gray-50 hover:bg-gray-100"
      }`}
    >
      <input
        type="file"
        accept="image/*,.pdf"
        capture="environment"
        onChange={onChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        data-testid="file-upload"
      />
      <UploadCloud className="w-12 h-12 text-gray-400 mb-4" />
      <p className="text-gray-600 font-medium text-center">
        거래명세서 촬영 또는 업로드<br />
        <span className="text-sm font-normal text-gray-500">(클릭하거나 파일을 드래그 앤 드롭)</span>
      </p>
    </div>
  );
}
