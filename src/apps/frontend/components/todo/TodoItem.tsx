import React from 'react';
import { Todo } from '../../types/todo';

type Props = {
  todo: Todo;
  onUpdateStatus: (id: string, status: 'To Do' | 'Done') => void;
  onDelete: (id: string) => void;
};

const TodoItem: React.FC<Props> = ({ todo, onUpdateStatus, onDelete }) => {
  return (
    <div className="border rounded p-3 my-2 flex justify-between items-center bg-white shadow-sm">
      <div>
        <h3 className="font-semibold">{todo.title}</h3>
        <p className="text-sm text-gray-600">{todo.description}</p>
        <p className="text-xs text-gray-500">
          Type: {todo.type} | Due:{' '}
          {new Date(todo.due_date).toLocaleDateString()}
        </p>
        <p className="text-xs text-gray-500">Status: {todo.status}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() =>
            onUpdateStatus(todo.id, todo.status === 'To Do' ? 'Done' : 'To Do')
          }
        >
          {todo.status === 'To Do' ? 'Mark Done' : 'Mark To Do'}
        </button>
        <button className="text-red-500" onClick={() => onDelete(todo.id)}>
          Delete
        </button>
      </div>
    </div>
  );
};

export default TodoItem;
