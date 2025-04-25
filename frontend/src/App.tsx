/* eslint-disable */
// @ts-nocheck
import { useState } from 'react';
import ColumnPicker from './ColumnPicker';

export default function App() {
  const [file, setFile] = useState(null);
  const [datasetId, setDatasetId] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [rows, setRows] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [evaluated, setEvaluated] = useState(false);
  const [uniqueCategories, setUniqueCategories] = useState([]);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setMessage('Uploading...');

    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();
      setDatasetId(uploadData.dataset_id);
      setMessage("Upload successful. Now select columns to evaluate.");
    } catch (error) {
      setMessage("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetMetrics = async () => {
    setLoading(true);
    const res = await fetch(`http://localhost:8000/dataset/${datasetId}/metrics`);
    const data = await res.json();
    setMetrics(data);
    setLoading(false);
  };

  const handleLoadRows = async () => {
    setLoading(true);
    setMessage("Loading rows for review...");
    try {
      const res = await fetch(`http://localhost:8000/dataset/${datasetId}/rows`);
      const data = await res.json();

      if (!Array.isArray(data)) {
        console.error("Expected array, got:", data);
        setMessage("❌ Failed to load rows: " + (data.message || "Unknown error"));
        return;
      }

      setRows(data);
      const categories = [...new Set(data.map(row => row.model_category))];
      setUniqueCategories(categories);
      setCurrentIndex(0);
      setMessage("");
    } catch (err) {
      setMessage("Failed to load rows: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFixCategory = async (index, newCategory) => {
    const row = rows[index];
    const res = await fetch(`http://localhost:8000/rows/${datasetId}/${row.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fixed_category: newCategory })
    });

    if (res.ok) {
      const updated = [...rows];
      updated[index].fixed_category = newCategory;
      setRows(updated);
    }
  };

  const handleExport = async () => {
    setMessage("Generating export file...");
  const trigger = await fetch(`http://localhost:8000/export/${datasetId}`, {
    method: "POST",
  });
  const result = await trigger.json();

  if (result.status !== "success") {
    setMessage("Failed to generate export: " + result.message);
    return;
  }

  setMessage("Downloading CSV...");
  const res = await fetch(`http://localhost:8000/export/${datasetId}`);
  if (res.ok) {
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${datasetId}_corrected.csv`;
    a.click();
    setMessage("Export complete");
  } else {
    setMessage("Download failed");
  }
};

  const currentBatch = rows.slice(currentIndex, currentIndex + 10);

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Dataset Class Review Tool</h1>

      {!datasetId && (
        <>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="mb-4"
          />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            {loading ? "Uploading..." : "Upload CSV"}
          </button>
        </>
      )}

      {datasetId && !evaluated && (
        <ColumnPicker datasetId={datasetId} onEvaluated={() => setEvaluated(true)} />
      )}

      {evaluated && (
        <div className="mt-4">
          <p><strong>Dataset ID:</strong> {datasetId}</p>
          <button
            onClick={handleGetMetrics}
            disabled={loading}
            className="mt-2 px-4 py-2 bg-green-500 text-white rounded mr-2"
          >
            {loading ? "Loading..." : "Get Metrics"}
          </button>
          <button
            onClick={handleLoadRows}
            disabled={loading}
            className="mt-2 px-4 py-2 bg-yellow-500 text-white rounded mr-2"
          >
            {loading ? "Loading..." : "Load for Review"}
          </button>
          <button
            onClick={handleExport}
            disabled={loading}
            className="mt-2 px-4 py-2 bg-purple-500 text-white rounded"
          >
            Export CSV
          </button>
        </div>
      )}

      {metrics && (
        <div className="mt-4">
          <h2 className="font-semibold">Metrics</h2>
          <ul className="list-disc list-inside">
            <li>Total: {metrics.total}</li>
            <li>Initial Accuracy: {metrics.accuracy_initial}%</li>
            <li>Initial Mistakes: {metrics.wrong_initial}</li>
            <li>Current Accuracy: {metrics.accuracy_current}%</li>
            <li>Current Mistakes: {metrics.wrong_current}</li>
          </ul>
        </div>
      )}

      {currentBatch.length > 0 && (
        <div className="mt-6">
          {currentBatch.map((row, index) => (
            <div key={row.id} className="border p-4 rounded shadow mb-4">
              <h3 className="font-bold mb-2">Row {currentIndex + index + 1} of {rows.length}</h3>
              <p className="mb-2"><strong>Text:</strong> {row.product_text}</p>
              <p className="mb-2"><strong>Model Prediction:</strong> {row.model_category}</p>
              <p className="mb-4"><strong>Fixed Category:</strong> {row.fixed_category || '—'}</p>
              <div className="space-x-2">
                {uniqueCategories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => handleFixCategory(currentIndex + index, cat)}
                    className="px-3 py-1 bg-blue-600 text-white rounded"
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <div className="flex justify-between mt-4">
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 10))}
              disabled={currentIndex === 0}
              className="px-4 py-2 bg-gray-400 text-white rounded"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentIndex(prev => Math.min(rows.length - 1, prev + 10))}
              disabled={currentIndex + 10 >= rows.length}
              className="px-4 py-2 bg-gray-600 text-white rounded"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {message && <p className="mt-4 text-yellow-600">{message}</p>}
    </div>
  );
}
