// src/services/todo.service.ts
import APIService from './api.service';

const api = new APIService();

export const getTodo = async () => {
  const response = await api.apiClient.get('/todos');

  // Transform MongoDB _id → id
  return response.data.map((todo: any) => ({
    ...todo,
    id: todo._id,
  }));
};
export const createTodo = async (data: {
  title: string;
  description: string;
  type: 'Official' | 'Personal' | 'Hobby';
  due_date: string;
}) => {
  return await api.apiClient.post('/todos', data);
};

export const updateTodo = async (
  id: string,
  data: { status?: 'To Do' | 'Done' },
) => {
  return await api.apiClient.put(`/todos/${id}`, data);
};

export const deleteTodo = async (id: string) => {
  return await api.apiClient.delete(`/todos/${id}`);
};
