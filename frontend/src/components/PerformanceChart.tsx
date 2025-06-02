import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format, parseISO } from 'date-fns';
import { apiService, PerformanceData, FilterOptions } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PerformanceChartProps {
  filters: FilterOptions;
  username: string;
  height?: number;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ 
  filters, 
  username,
  height = 560 
}) => {
  const [data, setData] = useState<PerformanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [hoverValues, setHoverValues] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const performanceData = await apiService.getPerformanceData(username, filters);
        setData(performanceData);
      } catch (err) {
        setError('Failed to fetch performance data');
        console.error('Error fetching performance data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters, username]);

  const calculateRollingAverage = (data: number[], window: number): number[] => {
    const result: number[] = [];
    for (let i = 0; i < data.length; i++) {
      const start = Math.max(0, i - window + 1);
      const slice = data.slice(start, i + 1);
      const average = slice.reduce((sum, val) => sum + val, 0) / slice.length;
      result.push(average);
    }
    return result;
  };

  const chartData = React.useMemo(() => {
    if (!data.length) return null;

    const rollingWindow = filters.rollingWindow || 10;
    const labels = data.map(d => format(parseISO(d.date), 'MMM dd'));
    
    const blunderRates = data.map(d => d.blunder_rate);
    const mistakeRates = data.map(d => d.mistake_rate);
    const inaccuracyRates = data.map(d => d.inaccuracy_rate);
    const userRatings = data.map(d => d.user_rating || 0);
    
    const rollingBlunders = calculateRollingAverage(blunderRates, rollingWindow);
    const rollingMistakes = calculateRollingAverage(mistakeRates, rollingWindow);
    const rollingInaccuracies = calculateRollingAverage(inaccuracyRates, rollingWindow);
    const rollingRatings = calculateRollingAverage(userRatings, rollingWindow);

    // Store max values from rolling averages for y-axis scaling
    const errorRateMax = Math.max(
      Math.max(...rollingBlunders), 
      Math.max(...rollingMistakes), 
      Math.max(...rollingInaccuracies)
    );
    const ratingMax = Math.max(...rollingRatings);
    const ratingMin = Math.min(...rollingRatings.filter(r => r > 0));

    // Calculate density (games per day or per rolling window)
    const densities = data.map(d => d.total_moves || 1); // fallback to 1 if missing

    // Simplified density-based line thickness
    const makeDensityDataset = (label: string, values: number[], color: string) => ({
      label,
      data: values.map((y, i) => ({ x: labels[i], y, density: densities[i] })),
      borderColor: color,
      backgroundColor: color + '10',
      borderWidth: 2,
      fill: false,
      tension: 0.4,
      yAxisID: 'y',
      pointRadius: 0,
      pointHoverRadius: 0,
      pointHitRadius: 10, // Larger invisible hit area for better hover detection
      segment: {
        borderWidth: ((ctx: any) => {
          const avgDensity = ((ctx.p0?.raw?.density || 1) + (ctx.p1?.raw?.density || 1)) / 2;
          return Math.max(1, Math.min(4, avgDensity / 15));
        }) as any
      }
    });

    return {
      labels,
      datasets: [
        // Rating line
        {
          label: `Rating`,
          data: rollingRatings.map((y, i) => ({ x: labels[i], y })),
          borderColor: '#2563eb',
          backgroundColor: '#2563eb10',
          borderWidth: 5, // Much thicker line
          fill: false,
          tension: 0.4,
          yAxisID: 'y1',
          pointRadius: 0,
          pointHoverRadius: 0,
          pointHitRadius: 10, // Larger invisible hit area for hover detection
          z: 10, // Higher z-index to ensure it stays on top
        },
        makeDensityDataset(`Blunder Rate`, rollingBlunders, '#dc2626'),
        makeDensityDataset(`Mistake Rate`, rollingMistakes, '#ea580c'),
        makeDensityDataset(`Inaccuracy Rate`, rollingInaccuracies, '#ca8a04'),
      ],
      // Add calculated bounds for axis scaling
      errorRateMax,
      ratingMax,
      ratingMin
    };
  }, [data, filters.rollingWindow]);

  // Enhanced hover handler with vertical line
  const handleHover = (event: any, activeElements: any[], chart: any) => {
    if (activeElements && activeElements.length > 0) {
      const index = activeElements[0].index;
      setHoverIndex(index);
      const values = chart.data.datasets.map((ds: any) => ds.data[index]?.y ?? null);
      setHoverValues(values);
    } else {
      setHoverIndex(null);
      setHoverValues(null);
    }
  };

  // Custom plugin to add background color to chart area only
  // Currently unused but kept for future styling enhancements
  // const chartAreaBackgroundPlugin = {
  //   id: 'chartAreaBackground',
  //   beforeDraw: (chart: any) => {
  //     const {
  //       ctx,
  //       chartArea: { left, top, width, height },
  //     } = chart;
      
      ctx.save();
      ctx.fillStyle = '#f8f9fa';
      ctx.fillRect(left, top, width, height);
      ctx.restore();
    },
  };

  const options: ChartOptions<'line'> = {
    animation: { duration: 0 }, // Disable animations for instant redraw
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: { top: 20, left: 20, right: 20, bottom: 80 }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#666',
          font: { size: 14 },
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 8,
          boxHeight: 8,
          padding: 20,
        },
      },
      title: {
        display: false,
      },
      tooltip: { 
        enabled: false,
        mode: 'index',
        intersect: false,
      },
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
    onHover: (event, elements, chart) => {
      // Make sure to call handleHover only when we have an event
      if (event && chart) {
        handleHover(event, elements, chart);
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
          color: '#666',
          font: { size: 16 },
        },
        grid: { 
          display: false,
        },
        ticks: { color: '#666', font: { size: 13 } },
        border: { display: false },
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Error Rate (%)',
          color: '#666',
          font: { size: 16 },
        },
        beginAtZero: false,
        min: 0, // Start at zero for error rates
        max: chartData?.errorRateMax ? chartData.errorRateMax * 1.1 : 10,
        grid: { 
          display: false,
        },
        ticks: { color: '#666', font: { size: 13 } },
        border: { display: false },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Rating',
          color: '#666',
          font: { size: 16 },
        },
        grid: { drawOnChartArea: false, display: false },
        // Use a tighter range for rating to make changes more visible
        min: chartData?.ratingMin ? chartData.ratingMin - 25 : 1000,
        max: chartData?.ratingMax ? chartData.ratingMax + 25 : 2000,
        ticks: { color: '#666', font: { size: 13 } },
        border: { display: false },
      },
    },
  };

  // Clean hover info display
  const renderHoverBar = () => {
    if (hoverIndex === null || !chartData) return null;
    const labels = chartData.labels as string[];
    const datasetLabels = chartData.datasets.map(ds => ds.label);
    const colors = ['#2563eb', '#dc2626', '#ea580c', '#ca8a04'];
    
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        background: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: 6,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        padding: '8px 16px',
        position: 'absolute',
        left: '50%',
        transform: 'translateX(-50%)',
        bottom: 20,
        zIndex: 10,
        fontSize: 13,
        whiteSpace: 'nowrap',
      }}>
        <span style={{ color: '#111', fontWeight: 500 }}>{labels[hoverIndex]}</span>
        {hoverValues && hoverValues.map((val: any, i: number) => (
          <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: colors[i],
              flexShrink: 0,
            }} />
            <span style={{ color: '#666', fontSize: 12 }}>{datasetLabels[i]}:</span>
            <span style={{ color: colors[i], fontWeight: 500 }}>
              {val !== null ? (i === 0 ? Math.round(val) : val.toFixed(1) + '%') : '--'}
            </span>
          </span>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-red-600 text-center">
          <p className="text-lg font-semibold">Error loading chart</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-gray-500 text-center">
          <p className="text-lg font-semibold">No data available</p>
          <p className="text-sm">Try adjusting your filters or analyzing more games</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      height, 
      position: 'relative', 
      background: '#ffffff',
      borderRadius: '8px',
      padding: '8px'
    }}>
      {renderHoverBar()}
      <Line 
        data={chartData} 
        options={options} 
        plugins={[
          {
            id: 'chartAreaBackground',
            beforeDraw: (chart: any) => {
              const {
                ctx,
                chartArea: { left, top, width, height },
              } = chart;
              
              ctx.save();
              ctx.fillStyle = '#f8f9fa';
              ctx.fillRect(left, top, width, height);
              ctx.restore();
            },
          },
          {
            id: 'verticalHoverLine',
            beforeDatasetsDraw: (chart: any) => {
              const ctx = chart.ctx;
              const active = (chart as any)._active || [];
              if (!active.length) return;
              const x = active[0].element.x;
              const top = chart.chartArea.top;
              const bottom = chart.chartArea.bottom;
              ctx.save();
              ctx.beginPath();
              ctx.strokeStyle = '#888888'; // solid grey line
              ctx.lineWidth = 4; // thicker line
              // draw solid line behind datasets
              ctx.moveTo(x, top);
              ctx.lineTo(x, bottom);
              ctx.stroke();
              ctx.restore();
            },
          }
        ]}
      />
    </div>
  );
};
