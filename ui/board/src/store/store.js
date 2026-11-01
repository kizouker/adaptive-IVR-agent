import { configureStore } from '@reduxjs/toolkit';
import boardReducer from './boardSlice';

const store = configureStore({
  reducer: {
    board: boardReducer,
  },
});

export default store;
