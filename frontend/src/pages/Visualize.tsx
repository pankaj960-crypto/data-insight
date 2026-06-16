import { useEffect, useRef, useState } from 'react';
import { Download } from 'lucide-react';
import { PlotlyChart, type PlotlyFigure } from '../components/PlotlyChart';
import { datasetService } from '../services/datasetService';
import type { Dataset } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

const CHART_TYPES = ['bar', 'line', 'pie', 'scatter', 'histogram', 'heatmap'];

function pickDefaultColumns(columnNames: string[], dtypes: Record<string, string>) {
  const numeric = columnNames.filter((c) => {
    const t = dtypes[c]?.toLowerCase() ?? '';
    return t.includes('int') || t.includes('float') || t.includes('number');
  });
  const categorical = columnNames.filter((c) => !numeric.includes(c));

  return {
    x: categorical[0] ?? columnNames[0] ?? '',
    y: numeric[0] ?? columnNames[1] ?? columnNames[0] ?? '',
  };
}

export function Visualize() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [chartType, setChartType] = useState('bar');
  const [xCol, setXCol] = useState('');
  const [yCol, setYCol] = useState('');
  const [plotData, setPlotData] = useState<PlotlyFigure | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const plotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    datasetService.list().then((res) => {
      setDatasets(res.data.datasets);
      if (res.data.datasets[0]) setSelectedId(res.data.datasets[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    datasetService.getAnalysis(selectedId).then((res) => {
      setColumns(res.data.column_names);
      const defaults = pickDefaultColumns(res.data.column_names, res.data.dtypes);
      setXCol(defaults.x);
      setYCol(defaults.y);
    });
  }, [selectedId]);

  const generateChart = async () => {
    if (!selectedId) return;
    setLoading(true);
    setError('');
    setPlotData(null);
    try {
      const { data } = await datasetService.createChart(selectedId, {
        chart_type: chartType,
        x_column: xCol,
        y_column: yCol,
        limit: 100,
      });
      const json = data.plotly_json as PlotlyFigure;
      if (!json?.data?.length) {
        throw new Error('Chart data was empty');
      }
      setPlotData(json);
    } catch (e: unknown) {
      const message =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (e as Error)?.message ||
        'Failed to generate chart. Check your column selections and try again.';
      setError(typeof message === 'string' ? message : 'Failed to generate chart.');
    } finally {
      setLoading(false);
    }
  };

  const downloadPNG = async () => {
    const el = plotRef.current?.querySelector('.js-plotly-plot') as HTMLElement & {
      emit?: (event: string, opts: object) => void;
    };
    if (el?.emit) {
      el.emit('plotly_downloadimage', { format: 'png', width: 1200, height: 800, filename: 'chart' });
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Visualizations</h1>
      <Card>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="text-sm font-medium">Dataset</label>
            <select
              value={selectedId ?? ''}
              onChange={(e) => setSelectedId(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Chart Type</label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700"
            >
              {CHART_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">X Axis</label>
            <select value={xCol} onChange={(e) => setXCol(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700">
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Y Axis</label>
            <select value={yCol} onChange={(e) => setYCol(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 dark:border-gray-600 dark:bg-gray-700">
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>
        {error && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
            {error}
          </p>
        )}
        <div className="mt-4 flex gap-2">
          <Button onClick={generateChart} loading={loading}>Generate Chart</Button>
          {plotData && (
            <Button variant="secondary" onClick={downloadPNG}>
              <Download className="mr-2 h-4 w-4" /> PNG
            </Button>
          )}
        </div>
      </Card>
      {plotData && (
        <Card>
          <div ref={plotRef}>
            <PlotlyChart figure={plotData} />
          </div>
        </Card>
      )}
    </div>
  );
}
