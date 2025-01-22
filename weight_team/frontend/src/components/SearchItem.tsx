import React, { useState } from 'react';
import {
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  LocalShipping as TruckIcon,
  Inventory as ContainerIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SearchItem = () => {
  const [open, setOpen] = useState(false);
  const [itemId, setItemId] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (itemId.trim()) {  // רק אם יש ID אחרי הסרת רווחים
      navigate(`/item/${itemId.trim()}`);  // הסר רווחים לפני הניווט
      setOpen(false);
      setItemId('');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // נקה רווחים בזמן ההקלדה
    setItemId(e.target.value.trim());
  };

  return (
    <>
      <Button
        variant="outlined"
        startIcon={<SearchIcon />}
        onClick={() => setOpen(true)}
        sx={{ ml: 2 }}
      >
        Search Item
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Search Item</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Enter Item ID"
            fullWidth
            variant="outlined"
            value={itemId}
            onChange={handleInputChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  {itemId.startsWith('T') ? 
                    <TruckIcon color="primary" /> : 
                    <ContainerIcon color="success" />
                  }
                </InputAdornment>
              ),
            }}
            placeholder="T123 for truck, C456 for container"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSearch} 
            variant="contained" 
            disabled={!itemId.trim()}
          >
            Search
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default SearchItem;