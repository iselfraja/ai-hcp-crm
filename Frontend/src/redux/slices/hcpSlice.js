import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const fetchHCPs = createAsyncThunk(
    'hcp/fetch',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/hcp');
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Fetch failed');
        }
    }
);

export const createHCP = createAsyncThunk(
    'hcp/create',
    async (data, { rejectWithValue }) => {
        try {
            const response = await api.post('/hcp', data);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data?.detail || 'Creation failed');
        }
    }
);

const hcpSlice = createSlice({
    name: 'hcp',
    initialState: {
        list: [],
        loading: false,
        error: null,
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchHCPs.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchHCPs.fulfilled, (state, action) => {
                state.loading = false;
                state.list = action.payload;
            })
            .addCase(fetchHCPs.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(createHCP.fulfilled, (state, action) => {
                state.list.push(action.payload);
            });
    },
});

export default hcpSlice.reducer;