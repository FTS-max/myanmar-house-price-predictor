'use client';

import { cn } from '@/lib/utils';
import React, { useEffect, useRef, useState } from 'react';

interface ChartDataPoint {
  label: string;
  value: number;
}

interface BarChartProps {
  data: ChartDataPoint[];
  height?: number;
  width?: number;
  barColor?: string;
  labelColor?: string;
  valueFormatter?: (value: number) => string;
  className?: string;
  showValues?: boolean;
}

export function BarChart({
  data,
  height = 300,
  width = 600,
  barColor = '#0070f3',
  labelColor = '#666',
  valueFormatter = (value) => value.toString(),
  className,
  showValues = true,
}: BarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(width);
  
  useEffect(() => {
    if (chartRef.current) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          setChartWidth(entry.contentRect.width);
        }
      });
      
      resizeObserver.observe(chartRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);
  
  const maxValue = Math.max(...data.map((item) => item.value));
  const barWidth = chartWidth / data.length - 10;
  
  return (
    <div 
      ref={chartRef}
      className={cn('w-full overflow-x-auto', className)}
      style={{ height: `${height}px`, minWidth: `${Math.max(width, 300)}px` }}
    >
      <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${height}`} preserveAspectRatio="none">
        {/* Y-axis and grid lines */}
        <line x1="40" y1="10" x2="40" y2={height - 30} stroke="#e5e5e5" strokeWidth="1" />
        
        {[0, 0.25, 0.5, 0.75, 1].map((tick, i) => {
          const y = height - 30 - (height - 40) * tick;
          return (
            <React.Fragment key={i}>
              <line x1="35" y1={y} x2="40" y2={y} stroke="#e5e5e5" strokeWidth="1" />
              <line x1="40" y1={y} x2={chartWidth - 10} y2={y} stroke="#e5e5e5" strokeWidth="1" strokeDasharray="4 4" />
              <text x="30" y={y + 4} textAnchor="end" fontSize="10" fill={labelColor}>
                {valueFormatter(maxValue * tick)}
              </text>
            </React.Fragment>
          );
        })}
        
        {/* Bars */}
        {data.map((item, i) => {
          const barHeight = ((height - 40) * item.value) / maxValue;
          const x = 50 + i * (barWidth + 10);
          const y = height - 30 - barHeight;
          
          return (
            <g key={i}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={barColor}
                rx="2"
                ry="2"
              />
              {showValues && (
                <text
                  x={x + barWidth / 2}
                  y={y - 5}
                  textAnchor="middle"
                  fontSize="10"
                  fill={labelColor}
                >
                  {valueFormatter(item.value)}
                </text>
              )}
              <text
                x={x + barWidth / 2}
                y={height - 10}
                textAnchor="middle"
                fontSize="10"
                fill={labelColor}
              >
                {item.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

interface LineChartProps {
  data: ChartDataPoint[];
  height?: number;
  width?: number;
  lineColor?: string;
  fillColor?: string;
  labelColor?: string;
  valueFormatter?: (value: number) => string;
  className?: string;
  showPoints?: boolean;
}

export function LineChart({
  data,
  height = 300,
  width = 600,
  lineColor = '#0070f3',
  fillColor = 'rgba(0, 112, 243, 0.1)',
  labelColor = '#666',
  valueFormatter = (value) => value.toString(),
  className,
  showPoints = true,
}: LineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(width);
  
  useEffect(() => {
    if (chartRef.current) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          setChartWidth(entry.contentRect.width);
        }
      });
      
      resizeObserver.observe(chartRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);
  
  const maxValue = Math.max(...data.map((item) => item.value));
  const minValue = Math.min(...data.map((item) => item.value));
  const normalizedMinValue = minValue > 0 ? 0 : minValue;
  const valueRange = maxValue - normalizedMinValue;
  
  // Generate points for the line
  const points = data.map((item, i) => {
    const x = 50 + (i * (chartWidth - 60)) / (data.length - 1);
    const y = height - 30 - ((item.value - normalizedMinValue) / valueRange) * (height - 40);
    return { x, y, value: item.value, label: item.label };
  });
  
  // Generate the path for the line
  const linePath = points.map((point, i) => {
    return i === 0 ? `M ${point.x} ${point.y}` : `L ${point.x} ${point.y}`;
  }).join(' ');
  
  // Generate the path for the area fill
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - 30} L ${points[0].x} ${height - 30} Z`;
  
  return (
    <div 
      ref={chartRef}
      className={cn('w-full overflow-x-auto', className)}
      style={{ height: `${height}px`, minWidth: `${Math.max(width, 300)}px` }}
    >
      <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${height}`} preserveAspectRatio="none">
        {/* Y-axis and grid lines */}
        <line x1="40" y1="10" x2="40" y2={height - 30} stroke="#e5e5e5" strokeWidth="1" />
        
        {[0, 0.25, 0.5, 0.75, 1].map((tick, i) => {
          const y = height - 30 - (height - 40) * tick;
          return (
            <React.Fragment key={i}>
              <line x1="35" y1={y} x2="40" y2={y} stroke="#e5e5e5" strokeWidth="1" />
              <line x1="40" y1={y} x2={chartWidth - 10} y2={y} stroke="#e5e5e5" strokeWidth="1" strokeDasharray="4 4" />
              <text x="30" y={y + 4} textAnchor="end" fontSize="10" fill={labelColor}>
                {valueFormatter(normalizedMinValue + valueRange * tick)}
              </text>
            </React.Fragment>
          );
        })}
        
        {/* X-axis */}
        <line x1="40" y1={height - 30} x2={chartWidth - 10} y2={height - 30} stroke="#e5e5e5" strokeWidth="1" />
        
        {/* Area fill */}
        <path d={areaPath} fill={fillColor} />
        
        {/* Line */}
        <path d={linePath} fill="none" stroke={lineColor} strokeWidth="2" />
        
        {/* Points and labels */}
        {points.map((point, i) => (
          <g key={i}>
            {showPoints && (
              <circle cx={point.x} cy={point.y} r="4" fill="white" stroke={lineColor} strokeWidth="2" />
            )}
            <text
              x={point.x}
              y={height - 10}
              textAnchor="middle"
              fontSize="10"
              fill={labelColor}
            >
              {point.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

interface PieChartProps {
  data: (ChartDataPoint & { color?: string })[];
  height?: number;
  width?: number;
  className?: string;
  valueFormatter?: (value: number) => string;
  showLegend?: boolean;
}

export function PieChart({
  data,
  height = 300,
  width = 300,
  className,
  valueFormatter = (value) => value.toString(),
  showLegend = true,
}: PieChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [chartSize, setChartSize] = useState({ width, height });
  
  useEffect(() => {
    if (chartRef.current) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const size = Math.min(entry.contentRect.width, height);
          setChartSize({ width: size, height: size });
        }
      });
      
      resizeObserver.observe(chartRef.current);
      return () => resizeObserver.disconnect();
    }
  }, [height]);
  
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const radius = Math.min(chartSize.width, chartSize.height) / 2 - 10;
  const centerX = chartSize.width / 2;
  const centerY = chartSize.height / 2;
  
  // Default colors if not provided
  const defaultColors = [
    '#0070f3', '#7928ca', '#ff4d4f', '#52c41a', '#faad14',
    '#13c2c2', '#722ed1', '#eb2f96', '#fa8c16', '#a0d911',
  ];
  
  // Generate pie slices
  let startAngle = 0;
  const slices = data.map((item, i) => {
    const percentage = item.value / total;
    const angle = percentage * 360;
    const endAngle = startAngle + angle;
    
    // Calculate the SVG arc path
    const startRad = (startAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);
    
    const x1 = centerX + radius * Math.cos(startRad);
    const y1 = centerY + radius * Math.sin(startRad);
    const x2 = centerX + radius * Math.cos(endRad);
    const y2 = centerY + radius * Math.sin(endRad);
    
    const largeArcFlag = angle > 180 ? 1 : 0;
    
    const pathData = [
      `M ${centerX} ${centerY}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ');
    
    // Calculate position for the label
    const labelRad = (startAngle + angle / 2 - 90) * (Math.PI / 180);
    const labelDistance = radius * 0.7;
    const labelX = centerX + labelDistance * Math.cos(labelRad);
    const labelY = centerY + labelDistance * Math.sin(labelRad);
    
    const color = item.color || defaultColors[i % defaultColors.length];
    
    const slice = {
      path: pathData,
      color,
      percentage,
      labelX,
      labelY,
      label: item.label,
      value: item.value,
    };
    
    startAngle = endAngle;
    return slice;
  });
  
  return (
    <div 
      ref={chartRef}
      className={cn('w-full', className)}
      style={{ height: `${height}px` }}
    >
      <div className="flex flex-col md:flex-row items-center">
        <svg width={chartSize.width} height={chartSize.height} viewBox={`0 0 ${chartSize.width} ${chartSize.height}`}>
          {slices.map((slice, i) => (
            <g key={i}>
              <path d={slice.path} fill={slice.color} stroke="white" strokeWidth="1" />
              {slice.percentage > 0.05 && (
                <text
                  x={slice.labelX}
                  y={slice.labelY}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize="12"
                  fontWeight="bold"
                >
                  {Math.round(slice.percentage * 100)}%
                </text>
              )}
            </g>
          ))}
        </svg>
        
        {showLegend && (
          <div className="mt-4 md:mt-0 md:ml-4 grid grid-cols-1 gap-2">
            {slices.map((slice, i) => (
              <div key={i} className="flex items-center">
                <div
                  className="w-4 h-4 mr-2"
                  style={{ backgroundColor: slice.color }}
                />
                <span className="text-sm">
                  {slice.label} ({valueFormatter(slice.value)})
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}