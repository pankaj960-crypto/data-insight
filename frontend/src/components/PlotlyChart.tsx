import { useEffect, useRef } from 'react';

export interface PlotlyFigure {
  data: object[];
  layout?: object;
}

type PlotlyModule = {
  newPlot: (el: HTMLElement, data: object[], layout: object, config?: object) => Promise<void>;
  purge: (el: HTMLElement) => void;
  relayout: (el: HTMLElement, layout: object) => void;
};

let plotlyPromise: Promise<PlotlyModule> | null = null;

function loadPlotly(): Promise<PlotlyModule> {
  if (!plotlyPromise) {
    plotlyPromise = import('plotly.js/dist/plotly.min.js').then((mod) => {
      const plotly = (mod as { default?: PlotlyModule }).default ?? (mod as unknown as PlotlyModule);
      return plotly;
    });
  }
  return plotlyPromise;
}

interface PlotlyChartProps {
  figure: PlotlyFigure;
  className?: string;
  height?: number;
}

export function PlotlyChart({ figure, className, height = 500 }: PlotlyChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el || !figure.data?.length) return;

    let active = true;

    loadPlotly()
      .then((Plotly) => {
        if (!active) return;
        return Plotly.newPlot(el, figure.data, figure.layout ?? {}, {
          responsive: true,
          displayModeBar: true,
        });
      })
      .catch((err) => {
        console.error('Plotly render failed:', err);
      });

    return () => {
      active = false;
      loadPlotly().then((Plotly) => {
        Plotly.purge(el);
      });
    };
  }, [figure]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: '100%', height: `${height}px` }}
    />
  );
}
