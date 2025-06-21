// frontend/types/index.ts

export type Todo = {
  id: string;
  user_id: string;
  title: string;
  description: string;
  type: 'Personal' | 'Official' | 'Hobby';
  due_date: string;
  status: 'To Do' | 'Done';
  created_at: string;
};
