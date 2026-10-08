"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getDocument, DocumentData } from "@/lib/api";
import ReviewField from "@/components/ReviewField";
import { Loader2 } from "lucide-react";
import { Suspense } from "react";

function ReviewPageContent() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<DocumentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDoc = async () => {
      try {
        const doc = await getDocument(params.id as string);
        setData(doc);
      } catch (err: unknown) {
        console.error(err);
        setError("데이터를 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    };
    if (params.id) fetchDoc();
  }, [params.id]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex flex-col h-screen items-center justify-center">
        <p className="text-red-500 mb-4">{error}</p>
        <button onClick={() => router.push("/")} className="text-blue-500 underline">
          처음으로 돌아가기
        </button>
      </div>
    );
  }

  const docId = data.document_id;

  const handleDataUpdated = (newData: unknown) => {
    setData(newData as DocumentData);
  };

  // Check if any field is in NEEDS_REVIEW status
  let hasNeedsReview = false;

  if (data.header) {
    Object.values(data.header).forEach(field => {
      if (field && field.validation_status === "NEEDS_REVIEW") {
        hasNeedsReview = true;
      }
    });
  }

  if (data.items) {
    data.items.forEach(item => {
      Object.values(item).forEach(field => {
        if (field && field.validation_status === "NEEDS_REVIEW") {
          hasNeedsReview = true;
        }
      });
    });
  }

  const handleErpSubmit = () => {
    if (hasNeedsReview) {
      alert("확인이 필요한 항목이 남아있습니다. 모두 확인/수정한 후 다시 시도해주세요.");
      return;
    }
    router.push(`/mock-erp/${docId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4 sm:p-8">
      <main className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 border-b pb-4">
          분석 결과 확인
        </h1>

        <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Header</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
            {data.header.order_type && <ReviewField docId={docId} label="발주구분" fieldName="order_type" data={data.header.order_type} onDataUpdated={handleDataUpdated} />}
            {data.header.vendor && <ReviewField docId={docId} label="거래처" fieldName="vendor" data={data.header.vendor} onDataUpdated={handleDataUpdated} />}
            {data.header.expected_receipt_date && <ReviewField docId={docId} label="입고예정일" fieldName="expected_receipt_date" data={data.header.expected_receipt_date} onDataUpdated={handleDataUpdated} />}
            {data.header.discount_rate && <ReviewField docId={docId} label="DC율" fieldName="discount_rate" data={data.header.discount_rate} onDataUpdated={handleDataUpdated} />}

            {/* Fallbacks for older phases */}
            {data.header.company_name && !data.header.vendor && <ReviewField docId={docId} label="회사명" fieldName="company_name" data={data.header.company_name} onDataUpdated={handleDataUpdated} />}
            {data.header.transaction_date && !data.header.expected_receipt_date && <ReviewField docId={docId} label="거래일자" fieldName="transaction_date" data={data.header.transaction_date} onDataUpdated={handleDataUpdated} />}
            {data.header.order_number && <ReviewField docId={docId} label="수주번호(헤더)" fieldName="order_number" data={data.header.order_number} onDataUpdated={handleDataUpdated} />}
            </div>
        </div>

        <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">품목 리스트 (Line Items)</h2>
        {data.items.map((item, index) => (
          <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-gray-700 mb-3">품목 {index + 1}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {item.order_number && <ReviewField docId={docId} itemIndex={index} label="수주번호" fieldName="order_number" data={item.order_number} onDataUpdated={handleDataUpdated} />}
              {item.item_number && <ReviewField docId={docId} itemIndex={index} label="품번" fieldName="item_number" data={item.item_number} onDataUpdated={handleDataUpdated} />}
              {item.item_name && <ReviewField docId={docId} itemIndex={index} label="품명" fieldName="item_name" data={item.item_name} onDataUpdated={handleDataUpdated} />}
              {item.specification && <ReviewField docId={docId} itemIndex={index} label="규격" fieldName="specification" data={item.specification} onDataUpdated={handleDataUpdated} />}
              {item.quantity && <ReviewField docId={docId} itemIndex={index} label="수량" fieldName="quantity" data={item.quantity} onDataUpdated={handleDataUpdated} />}
              {item.unit_quantity && <ReviewField docId={docId} itemIndex={index} label="단위수량" fieldName="unit_quantity" data={item.unit_quantity} onDataUpdated={handleDataUpdated} />}
              {item.unit_price && <ReviewField docId={docId} itemIndex={index} label="단가" fieldName="unit_price" data={item.unit_price} onDataUpdated={handleDataUpdated} />}
              {item.supply_amount && <ReviewField docId={docId} itemIndex={index} label="공급가액" fieldName="supply_amount" data={item.supply_amount} onDataUpdated={handleDataUpdated} />}

              {/* Fallback for older phases */}
              {item.discount_rate && <ReviewField docId={docId} itemIndex={index} label="DC율" fieldName="discount_rate" data={item.discount_rate} onDataUpdated={handleDataUpdated} />}
            </div>
          </div>
        ))}

        <div className="mt-8 flex justify-end space-x-4">
          <button onClick={() => router.push("/")} className="px-6 py-2 border rounded-md text-gray-600 hover:bg-gray-50">
            취소
          </button>
          <button
            onClick={handleErpSubmit}
            disabled={hasNeedsReview}
            className={`px-6 py-2 text-white rounded-md font-medium shadow-sm transition-colors ${hasNeedsReview ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            ERP 입력
          </button>
        </div>
      </main>
    </div>
  );
}

export default function ReviewPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>}>
      <ReviewPageContent />
    </Suspense>
  );
}
