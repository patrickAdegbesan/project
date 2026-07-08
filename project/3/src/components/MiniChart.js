import React from 'react';
import Svg, { Path, Circle, Line, Rect, Text as SvgText } from 'react-native-svg';
import { Colors } from '../theme';

// hex color + 2-char alpha suffix (00–FF)
function alpha(hex, pct) {
  const a = Math.round(pct * 255).toString(16).padStart(2, '0');
  return hex + a;
}

export function MiniLineChart({ data, width = 200, height = 60, color = Colors.chart_teal }) {
  if (!data || data.length < 2) return null;
  const padX = 8, padY = 8;
  const minY = Math.min(...data);
  const maxY = Math.max(...data);
  const rangeY = maxY - minY || 1;

  const toX = (i) => padX + (i / (data.length - 1)) * (width - padX * 2);
  const toY = (v) => padY + (1 - (v - minY) / rangeY) * (height - padY * 2);

  const pts = data.map((v, i) => ({ x: toX(i), y: toY(v) }));
  let d = `M ${pts[0].x} ${pts[0].y}`;
  for (let i = 1; i < pts.length; i++) {
    const cp = (pts[i - 1].x + pts[i].x) / 2;
    d += ` C ${cp} ${pts[i - 1].y}, ${cp} ${pts[i].y}, ${pts[i].x} ${pts[i].y}`;
  }
  const areaD = d + ` L ${pts[pts.length - 1].x} ${height} L ${pts[0].x} ${height} Z`;

  return (
    <Svg width={width} height={height} overflow="hidden">
      <Path d={areaD} fill={alpha(color, 0.12)} />
      <Path d={d} stroke={color} strokeWidth="2.5" fill="none" strokeLinecap="round" />
      {pts.map((p, i) => (
        <Circle key={i} cx={p.x} cy={p.y} r={i === pts.length - 1 ? 4 : 2.5} fill={color} />
      ))}
    </Svg>
  );
}

export function FullLineChart({
  dataSets = [],
  width = 340,
  height = 200,
  labels = [],
  goalValue,
  healthyBandMin,
  healthyBandMax,
}) {
  if (!dataSets.length || !dataSets[0].data.length) return null;

  const padX = 16;
  const padTop = 12;
  const padBottom = 22;
  const chartH = height - padTop - padBottom;

  const allValues = dataSets.flatMap((ds) => ds.data);
  if (goalValue      != null) allValues.push(goalValue);
  if (healthyBandMin != null) allValues.push(healthyBandMin);
  if (healthyBandMax != null) allValues.push(healthyBandMax);

  const minY   = Math.floor(Math.min(...allValues) - 3);
  const maxY   = Math.ceil(Math.max(...allValues) + 3);
  const rangeY = maxY - minY || 1;
  const dataLen = dataSets[0].data.length;

  const toX = (i) => padX + (i / Math.max(dataLen - 1, 1)) * (width - padX * 2);
  const toY = (v) => padTop + (1 - (v - minY) / rangeY) * chartH;

  const makePath = (data) => {
    const pts = data.map((v, i) => ({ x: toX(i), y: toY(v) }));
    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) {
      const cp = (pts[i - 1].x + pts[i].x) / 2;
      d += ` C ${cp} ${pts[i - 1].y}, ${cp} ${pts[i].y}, ${pts[i].x} ${pts[i].y}`;
    }
    return { d, pts };
  };

  const baselineY  = toY(minY);
  const bandMinY   = healthyBandMin != null ? toY(healthyBandMin) : null;
  const bandMaxY   = healthyBandMax != null ? toY(healthyBandMax) : null;
  const goalY      = goalValue      != null ? toY(goalValue)      : null;

  return (
    <Svg width={width} height={height} overflow="hidden">
      {/* Healthy band */}
      {bandMinY !== null && bandMaxY !== null && (
        <Rect
          x={padX} y={bandMaxY}
          width={width - padX * 2} height={bandMinY - bandMaxY}
          fill={alpha(Colors.accent, 0.10)}
          rx={3}
        />
      )}

      {/* Goal dashed line */}
      {goalY !== null && (
        <Line
          x1={padX} y1={goalY} x2={width - padX} y2={goalY}
          stroke={Colors.accent} strokeWidth="1.5" strokeDasharray="5,4"
        />
      )}

      {/* Data lines + area fills */}
      {dataSets.map((ds, di) => {
        const { d, pts } = makePath(ds.data);
        const areaD = d + ` L ${pts[pts.length - 1].x} ${baselineY} L ${pts[0].x} ${baselineY} Z`;
        return (
          <React.Fragment key={di}>
            {ds.showArea && <Path d={areaD} fill={alpha(ds.color, 0.14)} />}
            <Path d={d} stroke={ds.color} strokeWidth="2.5" fill="none" strokeLinecap="round" />
            {pts.map((p, pi) => (
              <Circle key={pi} cx={p.x} cy={p.y} r={3} fill={ds.color} />
            ))}
          </React.Fragment>
        );
      })}

      {/* X-axis labels */}
      {labels.map((l, i) => {
        const step = Math.max(1, Math.ceil(labels.length / 6));
        if (i % step !== 0 && i !== labels.length - 1) return null;
        return (
          <SvgText
            key={i}
            x={toX(i)}
            y={height - 4}
            textAnchor="middle"
            fontSize="9"
            fill={Colors.text3}
          >
            {l}
          </SvgText>
        );
      })}
    </Svg>
  );
}
