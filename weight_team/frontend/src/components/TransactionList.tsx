import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Chip,
  Divider,
  Stack
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
  SwapVert,
  OpenInNew
} from '@mui/icons-material';

type Direction = 'in' | 'out' | 'none';

interface WeightTransaction {
  id: string;
  direction: Direction;
  bruto: number;
  neto?: number | 'na';
  produce?: string;
  containers?: string[];
  truck?: string;
}

interface TransactionListProps {
  transactions: WeightTransaction[];
  loading: boolean;
}

const TransactionList: React.FC<TransactionListProps> = ({ transactions, loading }) => {
  const navigateToItem = (id: string) => {
    window.location.href = `/item/${id}`;
  };

  const navigateToSession = (id: string) => {
    window.location.href = `/session/${id}`;
  };

  const getDirectionIcon = (direction: Direction) => {
    switch (direction) {
      case 'in':
        return <ArrowDownward color="success" />;
      case 'out':
        return <ArrowUpward color="error" />;
      default:
        return <SwapVert color="disabled" />;
    }
  };

  const getDirectionColor = (direction: Direction) => {
    switch (direction) {
      case 'in':
        return 'success';
      case 'out':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Stack spacing={2}>
      {transactions.map((transaction) => (
        <Card key={transaction.id} variant="outlined">
          <CardContent>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, flex: 1 }}>
                {getDirectionIcon(transaction.direction)}
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="subtitle1" component="span">
                      ID: {transaction.id}
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<OpenInNew />}
                      onClick={() => navigateToSession(transaction.id)}
                      sx={{ ml: 1 }}
                    >
                      View Session
                    </Button>
                  </Box>
                  <Chip 
                    label={transaction.direction.toUpperCase()} 
                    color={getDirectionColor(transaction.direction)}
                    size="small"
                  />
                </Box>
              </Box>

              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: { xs: 'flex-start', sm: 'flex-end' },
                gap: 0.5
              }}>
                <Typography variant="body2">
                  <strong>Bruto:</strong> {transaction.bruto.toLocaleString()} kg
                </Typography>
                <Typography variant="body2">
                  <strong>Neto:</strong> {
                    transaction.neto === 'na' 
                      ? 'N/A' 
                      : `${transaction.neto?.toLocaleString()} kg`
                  }
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Produce:</strong> {transaction.produce || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Containers:</strong>{' '}
                  <Chip 
                    label={transaction.containers?.length || '0'} 
                    size="small" 
                    color="primary"
                    variant="outlined"
                  />
                </Typography>
              </Box>
              
              {transaction.truck && (
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<OpenInNew />}
                  onClick={() => navigateToItem(transaction.truck!)}
                >
                  View Truck
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
};

export default TransactionList;