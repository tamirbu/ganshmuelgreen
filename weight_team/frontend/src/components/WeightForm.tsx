import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WeightFormData } from '../types/api.types';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Typography,
  Paper,
  Grid,
  Alert,
  SelectChangeEvent,
  CircularProgress
} from '@mui/material';
import { Scale, ArrowBack } from '@mui/icons-material';

interface WeightFormProps {
  onSubmit: (data: WeightFormData) => Promise<void>;
}

const WeightForm: React.FC<WeightFormProps> = ({ onSubmit }) => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<WeightFormData>({
    direction: 'in',
    truck: '',
    containers: '',
    weight: 0,
    unit: 'kg',
    force: false,
    produce: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.weight) {
      errors.weight = 'Please enter weight';
    } else {
      const weightNum = Number(formData.weight);
      if (isNaN(weightNum)) {
        errors.weight = 'Weight must be a number';
      } else if (weightNum <= 0) {
        errors.weight = 'Weight must be greater than 0';
      } else if (weightNum > 99999) {
        errors.weight = 'Weight is too large';
      }
    }

    if (formData.direction !== 'none' && !formData.truck.trim()) {
      errors.truck = 'Please enter truck ID';
    }

    if (formData.direction !== 'none' && !formData.produce.trim()) {
      errors.produce = 'Please enter produce type';
    }

    if (formData.direction !== 'none' && formData.containers) {
      const containerIds = formData.containers.split(',').map(id => id.trim());
      const invalidContainers = containerIds.filter(id => !/^\d+$/.test(id));
      if (invalidContainers.length > 0) {
        errors.containers = 'Container IDs must be numbers only';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit({
        ...formData,
        weight: Number(formData.weight)
      });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Form submission error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent
  ) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 4, maxWidth: 'lg', mx: 'auto' }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/')}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Scale /> New Weight Measurement
        </Typography>
      </Box>

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="direction-label">Direction</InputLabel>
            <Select
              labelId="direction-label"
              name="direction"
              value={formData.direction}
              onChange={handleChange}
              label="Direction"
            >
              <MenuItem value="in">In</MenuItem>
              <MenuItem value="out">Out</MenuItem>
              <MenuItem value="none">None</MenuItem>
            </Select>
          </FormControl>

          {formData.direction !== 'none' && (
            <>
              <TextField
                fullWidth
                label="Truck ID"
                name="truck"
                value={formData.truck}
                onChange={handleChange}
                error={!!validationErrors.truck}
                helperText={validationErrors.truck}
                placeholder="Enter truck ID"
                variant="outlined"
              />

              <TextField
                fullWidth
                label="Containers"
                name="containers"
                value={formData.containers}
                onChange={handleChange}
                error={!!validationErrors.containers}
                helperText={validationErrors.containers}
                placeholder="Container IDs (comma separated)"
                variant="outlined"
              />
            </>
          )}

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Weight"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                error={!!validationErrors.weight}
                helperText={validationErrors.weight}
                inputProps={{ min: 1, max: 99999 }}
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="unit-label">Units</InputLabel>
                <Select
                  labelId="unit-label"
                  name="unit"
                  value={formData.unit}
                  onChange={handleChange}
                  label="Units"
                >
                  <MenuItem value="kg">kg</MenuItem>
                  <MenuItem value="lbs">lbs</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {formData.direction !== 'none' && (
            <TextField
              fullWidth
              label="Produce"
              name="produce"
              value={formData.produce}
              onChange={handleChange}
              error={!!validationErrors.produce}
              helperText={validationErrors.produce}
              placeholder="Enter produce type"
              variant="outlined"
            />
          )}

          <Box sx={{ display: 'flex', gap: 2, pt: 2 }}>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              fullWidth
              sx={{ py: 1.5 }}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Submitting...' : 'Submit Weight'}
            </Button>
            
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
              fullWidth
              sx={{ py: 1.5 }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
    </Paper>
  );
};

export default WeightForm;