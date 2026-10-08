"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2, CheckCircle2 } from "lucide-react";

interface ErpData {
  document_id: number;
  erp_header: {
    order_type?: string;
    vendor?: string;
    expected_receipt_date?: string;
    discount_rate?: string;
  };
  erp_items: Array<{
    order_number?: string;
    item_number?: string;
    item_name?: string;
    specification?: string;
    quantity?: string;
    unit_quantity?: string;
    unit_price?: string;
    supply_amount?: string;
  }>;
}

function MockErpContent() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<ErpData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    const fetchMapping = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/documents/${params.id}/erp-mapping`);
        if (!res.ok) {
          throw new Error("ERP 맵핑 데이터를 불러올 수 없습니다. (확인이 필요한 항목이 남아있을 수 있습니다)");
        }
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        console.error(err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    if (params.id) fetchMapping();
  }, [params.id]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/documents/${params.id}/submit-erp`, {
        method: "POST"
      });
      if (!res.ok) throw new Error("ERP 등록 실패");
      setIsSuccess(true);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex flex-col h-screen items-center justify-center bg-gray-100">
        <p className="text-red-500 mb-4">{error}</p>
        <button onClick={() => router.push(`/review/${params.id}`)} className="text-indigo-500 underline">
          리뷰 화면으로 돌아가기
        </button>
      </div>
    );
  }

  if (isSuccess) {
    return (
      <div className="flex flex-col h-screen items-center justify-center bg-gray-100">
        <CheckCircle2 className="w-16 h-16 text-green-500 mb-4" />
        <h1 className="text-2xl font-bold text-gray-800 mb-2">ERP 입력 성공</h1>
        <p className="text-gray-600 mb-6">Mock ERP 시스템에 데이터가 성공적으로 등록되었습니다.</p>
        <button onClick={() => router.push("/")} className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 shadow-sm">
          처음으로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-8 font-sans">
      <main className="max-w-6xl mx-auto bg-white rounded-md shadow-lg overflow-hidden border border-gray-200">
        <div className="bg-indigo-700 p-4 text-white flex justify-between items-center">
          <h1 className="text-xl font-bold tracking-wider">MOCK ERP SYSTEM</h1>
          <span className="text-indigo-200 text-sm">Session ID: {data.document_id}</span>
        </div>

        <div className="p-6">
          <div className="mb-6 flex justify-between items-end">
            <h2 className="text-lg font-bold text-gray-800 border-b-2 border-indigo-500 pb-1 inline-block">입고 등록</h2>
          </div>

          <div className="bg-gray-50 p-4 rounded-md border border-gray-200 mb-6">
            <h3 className="text-sm font-bold text-gray-600 mb-3 uppercase tracking-wider">Header Information</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">발주구분</label>
                <input type="text" readOnly value={data.erp_header.order_type || ''} className="w-full text-sm p-2 border border-gray-300 rounded bg-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">거래처</label>
                <input type="text" readOnly value={data.erp_header.vendor || ''} className="w-full text-sm p-2 border border-gray-300 rounded bg-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">입고예정일</label>
                <input type="text" readOnly value={data.erp_header.expected_receipt_date || ''} className="w-full text-sm p-2 border border-gray-300 rounded bg-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">DC율 (%)</label>
                <input type="text" readOnly value={data.erp_header.discount_rate || ''} className="w-full text-sm p-2 border border-gray-300 rounded bg-white" />
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-gray-600 mb-3 uppercase tracking-wider">Line Items</h3>
            <div className="overflow-x-auto border border-gray-200 rounded-md">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="text-xs text-gray-700 bg-gray-100 uppercase border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3">No.</th>
                    <th className="px-4 py-3">수주번호</th>
                    <th className="px-4 py-3">품번</th>
                    <th className="px-4 py-3">품명</th>
                    <th className="px-4 py-3">규격</th>
                    <th className="px-4 py-3 text-right">수량</th>
                    <th className="px-4 py-3 text-right">단위수량</th>
                    <th className="px-4 py-3 text-right">단가</th>
                    <th className="px-4 py-3 text-right">공급가액</th>
                  </tr>
                </thead>
                <tbody>
                  {data.erp_items.map((item, idx) => (
                    <tr key={idx} className="bg-white border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium text-gray-900">{idx + 1}</td>
                      <td className="px-4 py-2"><input type="text" readOnly value={item.order_number || ''} className="w-full bg-transparent outline-none" /></td>
                      <td className="px-4 py-2"><input type="text" readOnly value={item.item_number || ''} className="w-full bg-transparent outline-none" /></td>
                      <td className="px-4 py-2"><input type="text" readOnly value={item.item_name || ''} className="w-full bg-transparent outline-none" /></td>
                      <td className="px-4 py-2"><input type="text" readOnly value={item.specification || ''} className="w-full bg-transparent outline-none" /></td>
                      <td className="px-4 py-2 text-right"><input type="text" readOnly value={item.quantity || ''} className="w-full bg-transparent outline-none text-right" /></td>
                      <td className="px-4 py-2 text-right"><input type="text" readOnly value={item.unit_quantity || ''} className="w-full bg-transparent outline-none text-right" /></td>
                      <td className="px-4 py-2 text-right"><input type="text" readOnly value={item.unit_price || ''} className="w-full bg-transparent outline-none text-right" /></td>
                      <td className="px-4 py-2 text-right font-semibold text-gray-700"><input type="text" readOnly value={item.supply_amount || ''} className="w-full bg-transparent outline-none text-right font-semibold text-gray-700" /></td>
                    </tr>
                  ))}
                  {data.erp_items.length === 0 && (
                    <tr>
                      <td colSpan={9} className="px-4 py-8 text-center text-gray-500">품목 데이터가 없습니다.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 p-4 border-t border-gray-200 flex justify-end space-x-3">
          <button onClick={() => router.back()} disabled={isSubmitting} className="px-5 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50">
            취소
          </button>
          <button onClick={handleSubmit} disabled={isSubmitting} className="flex items-center px-6 py-2 text-sm font-medium text-white bg-indigo-600 rounded hover:bg-indigo-700 shadow-sm disabled:opacity-50">
            {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            저장 / 등록
          </button>
        </div>
      </main>
    </div>
  );
}

export default function MockErpPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>}>
      <MockErpContent />
    </Suspense>
  );
}
