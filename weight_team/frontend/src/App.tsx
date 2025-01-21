import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { WeightTransaction, WeightFormData } from './types/api.types';
import WeightForm from './components/WeightForm';
import TransactionList from './components/TransactionList';
import ItemDetails from './components/ItemDetails';
import SessionDetails from './components/SessionDetails';
import { weightService } from './services/api';
import { formatDateForAPI, getDaysAgo } from './utils/dateUtils';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Alert,
  Button,
  Paper,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

const App: React.FC = () => {
  const [transactions, setTransactions] = useState<WeightTransaction[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const fromDate = getDaysAgo(7);
      const toDate = new Date();

      const fromDateStr = formatDateForAPI(fromDate);
      const toDateStr = formatDateForAPI(toDate);

      const result = await weightService.getTransactions(fromDateStr, toDateStr);

      if (result.error) {
        throw new Error(result.error);
      }

      if (result.data) {
        setTransactions(result.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleSubmitWeight = async (formData: WeightFormData): Promise<void> => {
    const result = await weightService.submitWeight(formData);
    if (result.error) {
      throw new Error(result.error);
    }
    await fetchTransactions();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static" elevation={0}>
            <Toolbar>
              <Typography
                variant="h6"
                component={Link}
                to="/"
                sx={{
                  textDecoration: 'none',
                  color: 'inherit',
                  flexGrow: 1,
                  '&:hover': {
                    color: 'rgba(255, 255, 255, 0.9)',
                  },
                }}
              >
                Weight Management System
              </Typography>
            </Toolbar>
          </AppBar>

          <Container component="main" maxWidth="lg" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
            {error && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                onClose={() => setError(null)}
              >
                {error}
              </Alert>
            )}

            <Routes>
              <Route
                path="/"
                element={
                  <Paper elevation={0} sx={{ p: 3 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      mb: 3 
                    }}>
                      <Typography variant="h5" component="h1">
                        Recent Transactions
                      </Typography>
                      <Button
                        component={Link}
                        to="/add"
                        variant="contained"
                        startIcon={<AddIcon />}
                        sx={{
                          borderRadius: 2,
                        }}
                      >
                        Add Transaction
                      </Button>
                    </Box>
                    <TransactionList
                      transactions={transactions}
                      loading={loading}
                    />
                  </Paper>
                }
              />
              <Route
                path="/add"
                element={
                  <Paper elevation={0} sx={{ p: 3 }}>
                    <Typography variant="h5" component="h1" sx={{ mb: 3 }}>
                      New Transaction
                    </Typography>
                    <WeightForm onSubmit={handleSubmitWeight} />
                  </Paper>
                }
              />
              <Route
                path="/item/:id"
                element={
                  <Paper elevation={0} sx={{ p: 3 }}>
                    <ItemDetails />
                  </Paper>
                }
              />
              <Route
                path="/session/:id"
                element={
                  <Paper elevation={0} sx={{ p: 3 }}>
                    <SessionDetails />
                  </Paper>
                }
              />
            </Routes>
          </Container>

          <Box
            component="footer"
            sx={{
              py: 3,
              px: 2,
              mt: 'auto',
              backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[200]
                  : theme.palette.grey[800],
            }}
          >
            <Container maxWidth="lg">
              <Typography variant="body2" color="text.secondary" align="center">
                © {new Date().getFullYear()} Weight Management System
              </Typography>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;