// import React, { useState, useEffect } from 'react';
// import {
//   Box,
//   Paper,
//   Typography,
//   CircularProgress,
//   Alert,
//   Button,
//   Divider,
//   Card,
//   CardContent
// } from '@mui/material';
// import {
//   LocalShipping as TruckIcon,
//   Inventory as PackageIcon,
//   OpenInNew as ExternalLinkIcon
// } from '@mui/icons-material';

// interface ItemData {
//   id: string;
//   tara: number | 'na';
//   sessions: string[];
// }

// const ItemDetails = () => {
//   const [itemData, setItemData] = useState<ItemData | null>(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   // Get ID from URL
//   const id = window.location.pathname.split('/').pop() || '';

//   useEffect(() => {
//     const fetchItemDetails = async () => {
//       if (!id) return;

//       setLoading(true);
//       try {
//         const response = await fetch(`/api/item/${id}`);
//         if (!response.ok) {
//           throw new Error('Failed to fetch item details');
//         }
//         const data = await response.json();
//         setItemData(data);
//       } catch (err) {
//         setError(err instanceof Error ? err.message : 'An error occurred');
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchItemDetails();
//   }, [id]);

//   if (loading) {
//     return (
//       <Box display="flex" justifyContent="center" p={4}>
//         <CircularProgress />
//       </Box>
//     );
//   }

//   if (error) {
//     return (
//       <Alert severity="error" sx={{ mb: 2 }}>
//         {error}
//       </Alert>
//     );
//   }

//   if (!itemData) {
//     return (
//       <Alert severity="info" sx={{ mb: 2 }}>
//         No data found
//       </Alert>
//     );
//   }

//   const navigateToSession = (sessionId: string) => {
//     window.location.href = `/session/${sessionId}`;
//   };

//   return (
//     <Paper elevation={2} sx={{ p: 4 }}>
//       <Box display="flex" alignItems="center" gap={2} mb={3}>
//         {itemData.id.startsWith('T') ? (
//           <TruckIcon sx={{ fontSize: 40, color: 'primary.main' }} />
//         ) : (
//           <PackageIcon sx={{ fontSize: 40, color: 'success.main' }} />
//         )}
//         <Box>
//           <Typography variant="h5" component="h2">
//             {itemData.id}
//           </Typography>
//           <Typography color="text.secondary">
//             {itemData.id.startsWith('T') ? 'Truck' : 'Container'}
//           </Typography>
//         </Box>
//       </Box>

//       <Divider sx={{ my: 3 }} />

//       <Box sx={{ mb: 4 }}>
//         <Typography variant="subtitle2" color="text.secondary" gutterBottom>
//           Tara Weight
//         </Typography>
//         <Typography variant="h6">
//           {itemData.tara === "na" ? "Not Available" : `${itemData.tara} kg`}
//         </Typography>
//       </Box>

//       <Box>
//         <Typography variant="subtitle2" color="text.secondary" gutterBottom>
//           Recent Sessions
//         </Typography>
//         <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
//           {itemData.sessions.length > 0 ? (
//             itemData.sessions.map((session) => (
//               <Card key={session} variant="outlined">
//                 <CardContent sx={{ 
//                   display: 'flex', 
//                   justifyContent: 'space-between', 
//                   alignItems: 'center',
//                   '&:last-child': { pb: 2 }
//                 }}>
//                   <Typography variant="body2">
//                     Session ID: {session}
//                   </Typography>
//                   <Button
//                     startIcon={<ExternalLinkIcon />}
//                     onClick={() => navigateToSession(session)}
//                     size="small"
//                   >
//                     View Details
//                   </Button>
//                 </CardContent>
//               </Card>
//             ))
//           ) : (
//             <Typography color="text.secondary">No sessions found</Typography>
//           )}
//         </Box>
//       </Box>
//     </Paper>
//   );
// };
// export default ItemDetails;
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Divider,
  Card,
  CardContent,
  Stack
} from '@mui/material';
import {
  LocalShipping as TruckIcon,
  Inventory as PackageIcon,
  OpenInNew as ExternalLinkIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';

interface ItemData {
  id: string;
  tara: number | 'na';
  sessions: string[];
}

const ItemDetails = () => {
  const [itemData, setItemData] = useState<ItemData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get ID from URL
  const id = window.location.pathname.split('/').pop() || '';

  useEffect(() => {
    const fetchItemDetails = async () => {
      if (!id) return;

      setLoading(true);
      try {
        const response = await fetch(`/api/item/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch item details');
        }
        const data = await response.json();
        setItemData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchItemDetails();
  }, [id]);

  const navigateToSession = (sessionId: string) => {
    window.location.href = `/session/${sessionId}`;
  };

  const navigateToTruck = (truckId: string) => {
    window.location.href = `/truck/${truckId}`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!itemData) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        No data found
      </Alert>
    );
  }

  const isTruck = itemData.id.startsWith('T');

  return (
    <Paper elevation={2} sx={{ p: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          {isTruck ? (
            <TruckIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          ) : (
            <PackageIcon sx={{ fontSize: 40, color: 'success.main' }} />
          )}
          <Box>
            <Typography variant="h5" component="h2">
              {itemData.id}
            </Typography>
            <Typography color="text.secondary">
              {isTruck ? 'Truck' : 'Container'}
            </Typography>
          </Box>
        </Box>
        {isTruck && (
          <Button
            variant="outlined"
            startIcon={<ViewIcon />}
            onClick={() => navigateToTruck(itemData.id)}
          >
            View Truck Details
          </Button>
        )}
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Tara Weight
        </Typography>
        <Typography variant="h6">
          {itemData.tara === "na" ? "Not Available" : `${itemData.tara} kg`}
        </Typography>
      </Box>

      <Box>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Recent Sessions
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {itemData.sessions.length > 0 ? (
            itemData.sessions.map((session) => (
              <Card key={session} variant="outlined">
                <CardContent sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  '&:last-child': { pb: 2 }
                }}>
                  <Typography variant="body2">
                    Session ID: {session}
                  </Typography>
                  <Button
                    startIcon={<ExternalLinkIcon />}
                    onClick={() => navigateToSession(session)}
                    size="small"
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <Typography color="text.secondary">No sessions found</Typography>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default ItemDetails;