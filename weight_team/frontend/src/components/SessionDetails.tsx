import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Divider,
  Card,
  CardContent
} from '@mui/material';
import {
  Scale as ScaleIcon
} from '@mui/icons-material';

interface SessionData {
  id: string;
  truck: string;
  bruto: number;
  truckTara?: number;
  neto?: number | "na";
}

const SessionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessionDetails = async () => {
      try {
        const response = await fetch(`/api/session/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch session details');
        }
        const data = await response.json();
        setSessionData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchSessionDetails();
  }, [id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!sessionData) {
    return (
      <Alert severity="info">
        No session data found
      </Alert>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 4 }}>
      <Box display="flex" alignItems="center" gap={2} mb={4}>
        <ScaleIcon sx={{ fontSize: 40, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" component="h2">
            Session {sessionData.id}
          </Typography>
          <Typography color="text.secondary">
            Truck ID: {sessionData.truck === "na" ? "Not Available" : sessionData.truck}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Bruto Weight
              </Typography>
              <Typography variant="h6">
                {sessionData.bruto} kg
              </Typography>
            </Box>

            {sessionData.truckTara && (
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Truck Tara
                </Typography>
                <Typography variant="h6">
                  {sessionData.truckTara} kg
                </Typography>
              </Box>
            )}

            {sessionData.neto && (
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Neto Weight
                </Typography>
                <Typography variant="h6">
                  {sessionData.neto === "na" ? "Not Available" : `${sessionData.neto} kg`}
                </Typography>
              </Box>
            )}
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Weight Summary
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                {sessionData.neto && sessionData.neto !== "na" && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography>Net Weight:</Typography>
                    <Typography fontWeight="medium">{sessionData.neto} kg</Typography>
                  </Box>
                )}
                <Box display="flex" justifyContent="space-between">
                  <Typography>Gross Weight:</Typography>
                  <Typography fontWeight="medium">{sessionData.bruto} kg</Typography>
                </Box>
                {sessionData.truckTara && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography>Tara Weight:</Typography>
                    <Typography fontWeight="medium">{sessionData.truckTara} kg</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default SessionDetails;
