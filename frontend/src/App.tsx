import { useState, useEffect } from 'react';

export default function App() {
  const [file, setFile] = useState(null);
  const [datasetId, setDatasetId] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [rows, setRows] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

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
      const newDatasetId = uploadData.dataset_id;
      setDatasetId(newDatasetId);
      setMessage("Upload successful. Evaluating dataset...");

      const evalRes = await fetch(`http://localhost:8000/evaluate/${newDatasetId}`, {
        method: "POST",
      });

      const evalData = await evalRes.json();
      if (evalData.status === "success") {
        setMessage("Dataset evaluated successfully. You can now view metrics.");
      } else {
        setMessage("Evaluation failed: " + evalData.message);
      }
    } catch (error) {
      setMessage("Upload or evaluation failed.");
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
    const res = await fetch(`./local_data/db/${datasetId}_rows.json`);
    const data = await res.json();
    setRows(data);
    setCurrentIndex(0);
    setLoading(false);
  };

  const handleFixCategory = async (newCategory) => {
    const row = rows[currentIndex];
    const res = await fetch(`http://localhost:8000/rows/${datasetId}/${row.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fixed_category: newCategory })
    });

    if (res.ok) {
      const updated = [...rows];
      updated[currentIndex].fixed_category = newCategory;
      setRows(updated);
      if (currentIndex < rows.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        setMessage("Review complete. Run export_local(datasetId) in backend.");
      }
    }
  };

  const current = rows[currentIndex];

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

      {datasetId && (
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
            className="mt-2 px-4 py-2 bg-yellow-500 text-white rounded"
          >
            {loading ? "Loading..." : "Load for Review"}
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

      {current && (
        <div className="mt-6 border p-4 rounded shadow">
          <h3 className="font-bold mb-2">Reviewing Row {currentIndex + 1} of {rows.length}</h3>
          <p className="mb-2"><strong>Text:</strong> {current.product_text}</p>
          <p className="mb-2"><strong>Model Prediction:</strong> {current.model_category}</p>
          <p className="mb-4"><strong>Fixed Category:</strong> {current.fixed_category || '—'}</p>

          <input
            type="text"
            placeholder="Enter correct category"
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleFixCategory(e.target.value);
            }}
            className="px-2 py-1 border rounded w-full"
          />
        </div>
      )}

      {message && <p className="mt-4 text-yellow-600">{message}</p>}
    </div>
  );
}