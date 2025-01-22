// services/api.ts
import { 
  WeightFormData, 
  WeightTransaction, 
  SessionData, 
  ItemData,
  ApiResponse 
} from '../types/api.types';

export const weightService = {
  async getTransactions(from: string, to: string): Promise<ApiResponse<WeightTransaction[]>> {
    try {
      const response = await fetch(
        `/api/weight?from=${from}&to=${to}&filter=in,out`
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch transactions');
      }
      
      const data = await response.json();
      return { data };
    } catch (error) {
      return { 
        error: error instanceof Error ? error.message : 'An error occurred' 
      };
    }
  },

  async submitWeight(formData: WeightFormData): Promise<ApiResponse<{ session_id: string }>> {
    try {
      const response = await fetch('/api/weight', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to submit weight');
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return { 
        error: error instanceof Error ? error.message : 'Failed to submit weight' 
      };
    }
  },

  async getItemDetails(id: string): Promise<ApiResponse<ItemData>> {
    try {
      const response = await fetch(`/api/item/${id}`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch item details');
      }
      
      const data = await response.json();
      return { data };
    } catch (error) {
      return { 
        error: error instanceof Error ? error.message : 'An error occurred' 
      };
    }
  },

  async getSessionDetails(id: string): Promise<ApiResponse<SessionData>> {
    try {
      const response = await fetch(`/api/session/${id}`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch session details');
      }
      
      const data = await response.json();
      return { data };
    } catch (error) {
      return { 
        error: error instanceof Error ? error.message : 'An error occurred' 
      };
    }
  }
};