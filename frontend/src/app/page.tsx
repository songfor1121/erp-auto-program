import UploadArea from "@/components/UploadArea";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <main className="max-w-md w-full bg-white rounded-xl shadow-md overflow-hidden p-6">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">
          거래명세서 자동입력
        </h1>
        <UploadArea />
      </main>
    </div>
  );
}
