// types/api.types.ts

export type Direction = 'in' | 'out' | 'none';
export type WeightUnit = 'kg' | 'lbs';

export interface WeightTransaction {
  id: string;
  direction: Direction;
  bruto: number;
  neto?: number | 'na';
  produce?: string;
  containers?: string[];
  truck?: string;
}

export interface WeightFormData {
  direction: Direction;
  truck: string;
  containers: string;
  weight: number;
  unit: WeightUnit;
  force: boolean;
  produce: string;
}
export interface ItemData {
  id: string;
  tara: number | 'na';
  sessions: string[];
}
export interface SessionData {
  id: string;
  truck: string;
  bruto: number;
  direction: Direction;
  truckTara?: number;
  neto?: number | 'na';
  produce?: string;
  containers?: string[];
}

export interface ItemData {
  id: string;
  tara: number | 'na';
  sessions: string[];
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface ApiError {
  error: string;
}