import { useState, useEffect } from 'react';

// @ts-ignore
export default function ColumnPicker({ datasetId, onEvaluated }) {
  const [columns, setColumns] = useState([]);
  const [productColumn, setProductColumn] = useState('');
  const [categoryColumn, setCategoryColumn] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!datasetId) return;
    fetch(`http://localhost:8000/columns/${datasetId}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setColumns(data.columns);
        } else {
          setMessage('Failed to load columns: ' + data.message);
        }
      });
  }, [datasetId]);

  const handleEvaluate = async () => {
    if (!productColumn || !categoryColumn) {
      setMessage('Please select both product and category columns.');
      return;
    }
    setLoading(true);
    const res = await fetch(
      `http://localhost:8000/evaluate/${datasetId}?product_column=${productColumn}&category_column=${categoryColumn}`,
      { method: 'POST' }
    );
    const result = await res.json();
    if (result.status === 'success') {
      setMessage('Evaluation complete');
      onEvaluated();
    } else {
      setMessage('X ' + result.message);
    }
    setLoading(false);
  };

  return (
    <div className="mt-4 border p-4 rounded shadow">
      <h2 className="font-bold mb-2">Select Columns for Evaluation</h2>

      <label className="block mb-2">
        Product Column:
        <select
          className="w-full p-2 border rounded"
          value={productColumn}
          onChange={e => setProductColumn(e.target.value)}
        >
          <option value="">-- Select --</option>
          {columns.map(col => (
            <option key={col} value={col}>{col}</option>
          ))}
        </select>
      </label>

      <label className="block mb-2">
        Category Column:
        <select
          className="w-full p-2 border rounded"
          value={categoryColumn}
          onChange={e => setCategoryColumn(e.target.value)}
        >
          <option value="">-- Select --</option>
          {columns.map(col => (
            <option key={col} value={col}>{col}</option>
          ))}
        </select>
      </label>

      <button
        onClick={handleEvaluate}
        disabled={loading}
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
      >
        {loading ? 'Evaluating...' : 'Run Evaluation'}
      </button>

      {message && <p className="mt-2 text-yellow-700">{message}</p>}
    </div>
  );
}
