import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { WeightTransaction } from '../types/api.types';
import { Paper, Typography, Box } from '@mui/material';

interface WeightChartProps {
  transactions: WeightTransaction[];
}

const WeightChart: React.FC<WeightChartProps> = ({ transactions }) => {
  const chartData = transactions.map(t => ({
    id: t.id,
    bruto: t.bruto,
    neto: t.neto || 0
  }));

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Weight Analytics
      </Typography>
      <Box sx={{ height: 300, width: '100%' }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="id" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="bruto" 
              stroke="#1976d2" 
              name="Bruto Weight"
            />
            <Line 
              type="monotone" 
              dataKey="neto" 
              stroke="#2e7d32" 
              name="Neto Weight"
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default WeightChart;