import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

export const fetchBoard = createAsyncThunk('board/fetchBoard', async () => {
  const res = await fetch('/board-state.json');
  if (!res.ok) {
    throw new Error(`board fetch failed: ${res.status}`);
  }
  return res.json();
});

const initialState = {
  data: null, lang: 'sv', status: 'idle', error: null,
};

const boardSlice = createSlice({
  name: 'board',
  initialState,
  reducers: {
    setLang(state, action) {
      state.lang = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBoard.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchBoard.fulfilled, (state, action) => {
        state.status = 'ok';
        state.data = action.payload;
      })
      .addCase(fetchBoard.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { setLang } = boardSlice.actions;
export default boardSlice.reducer;
