import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import { Task, TaskFormData, TaskValidationError } from 'frontend/types';
import TaskService, { TaskFilters, TaskListResponse } from 'frontend/services/task.service';

// State interface
interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  pagination: {
    totalCount: number;
    totalPages: number;
    currentPage: number;
    pageSize: number;
    hasMore: boolean;
  };
  filters: TaskFilters;
  searchQuery: string;
  // Form states
  creatingTask: boolean;
  updatingTask: boolean;
  deletingTask: boolean;
  // Selected task for editing
  selectedTask: Task | null;
  showCreateForm: boolean;
  showEditForm: boolean;
}

// Action types
type TaskAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_TASKS'; payload: { tasks: Task[]; append?: boolean } }
  | { type: 'SET_PAGINATION'; payload: Partial<TaskState['pagination']> }
  | { type: 'SET_FILTERS'; payload: Partial<TaskFilters> }
  | { type: 'SET_SEARCH_QUERY'; payload: string }
  | { type: 'ADD_TASK'; payload: Task }
  | { type: 'UPDATE_TASK'; payload: Task }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'SET_CREATING_TASK'; payload: boolean }
  | { type: 'SET_UPDATING_TASK'; payload: boolean }
  | { type: 'SET_DELETING_TASK'; payload: boolean }
  | { type: 'SET_SELECTED_TASK'; payload: Task | null }
  | { type: 'SET_SHOW_CREATE_FORM'; payload: boolean }
  | { type: 'SET_SHOW_EDIT_FORM'; payload: boolean }
  | { type: 'RESET_STATE' };

// Initial state
const initialState: TaskState = {
  tasks: [],
  loading: false,
  error: null,
  pagination: {
    totalCount: 0,
    totalPages: 0,
    currentPage: 1,
    pageSize: 10,
    hasMore: false,
  },
  filters: {
    status: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  },
  searchQuery: '',
  creatingTask: false,
  updatingTask: false,
  deletingTask: false,
  selectedTask: null,
  showCreateForm: false,
  showEditForm: false,
};

// Reducer
const taskReducer = (state: TaskState, action: TaskAction): TaskState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };

    case 'SET_TASKS':
      const { tasks, append = false } = action.payload;
      return {
        ...state,
        tasks: append ? [...state.tasks, ...tasks] : tasks,
      };

    case 'SET_PAGINATION':
      return {
        ...state,
        pagination: {
          ...state.pagination,
          ...action.payload,
        },
      };

    case 'SET_FILTERS':
      return {
        ...state,
        filters: {
          ...state.filters,
          ...action.payload,
        },
      };

    case 'SET_SEARCH_QUERY':
      return {
        ...state,
        searchQuery: action.payload,
      };

    case 'ADD_TASK':
      return {
        ...state,
        tasks: [action.payload, ...state.tasks],
        pagination: {
          ...state.pagination,
          totalCount: state.pagination.totalCount + 1,
        },
      };

    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? action.payload : task
        ),
      };

    case 'DELETE_TASK':
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload),
        pagination: {
          ...state.pagination,
          totalCount: Math.max(0, state.pagination.totalCount - 1),
        },
      };

    case 'SET_CREATING_TASK':
      return {
        ...state,
        creatingTask: action.payload,
      };

    case 'SET_UPDATING_TASK':
      return {
        ...state,
        updatingTask: action.payload,
      };

    case 'SET_DELETING_TASK':
      return {
        ...state,
        deletingTask: action.payload,
      };

    case 'SET_SELECTED_TASK':
      return {
        ...state,
        selectedTask: action.payload,
      };

    case 'SET_SHOW_CREATE_FORM':
      return {
        ...state,
        showCreateForm: action.payload,
        if (action.payload) {
          showEditForm: false,
          selectedTask: null,
        },
      };

    case 'SET_SHOW_EDIT_FORM':
      return {
        ...state,
        showEditForm: action.payload,
        if (action.payload) {
          showCreateForm: false,
        },
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
};

// Context
interface TaskContextType {
  state: TaskState;
  actions: {
    loadTasks: (accountId: string, page?: number, append?: boolean) => Promise<void>;
    createTask: (accountId: string, data: TaskFormData) => Promise<void>;
    updateTask: (accountId: string, taskId: string, data: TaskFormData) => Promise<void>;
    deleteTask: (accountId: string, taskId: string) => Promise<void>;
    searchTasks: (accountId: string, query: string) => Promise<void>;
    setFilters: (filters: Partial<TaskFilters>) => void;
    setSearchQuery: (query: string) => void;
    showCreateForm: () => void;
    hideCreateForm: () => void;
    showEditForm: (task: Task) => void;
    hideEditForm: () => void;
    selectTask: (task: Task | null) => void;
    clearError: () => void;
    refreshTasks: (accountId: string) => Promise<void>;
  };
}

const TaskContext = createContext<TaskContextType | null>(null);

// Provider
interface TaskProviderProps {
  accountId: string;
  children: ReactNode;
}

export const TaskProvider: React.FC<TaskProviderProps> = ({ accountId, children }) => {
  const [state, dispatch] = useReducer(taskReducer, initialState);
  const taskService = new TaskService();

  const loadTasks = useCallback(async (acctId: string, page: number = 1, append: boolean = false) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const paginationParams = { page, size: state.pagination.pageSize, offset: (page - 1) * state.pagination.pageSize };
      const response = await taskService.getTasks(acctId, paginationParams, {
        ...state.filters,
        search: state.searchQuery || undefined,
      });

      if (response.data) {
        dispatch({ type: 'SET_TASKS', payload: { tasks: response.data.items, append } });
        dispatch({ type: 'SET_PAGINATION', payload: {
          totalCount: response.data.totalCount,
          totalPages: response.data.totalPages,
          currentPage: page,
          hasMore: page < response.data.totalPages,
        }});
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load tasks';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      console.error('Error loading tasks:', error);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.filters, state.pagination.pageSize, state.searchQuery, taskService]);

  const createTask = useCallback(async (acctId: string, data: TaskFormData) => {
    try {
      dispatch({ type: 'SET_CREATING_TASK', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await taskService.createTask(acctId, data.title, data.description);

      if (response.data) {
        dispatch({ type: 'ADD_TASK', payload: response.data });
        dispatch({ type: 'SET_SHOW_CREATE_FORM', payload: false });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      console.error('Error creating task:', error);
      throw error;
    } finally {
      dispatch({ type: 'SET_CREATING_TASK', payload: false });
    }
  }, [taskService]);

  const updateTask = useCallback(async (acctId: string, taskId: string, data: TaskFormData) => {
    try {
      dispatch({ type: 'SET_UPDATING_TASK', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await taskService.updateTask(acctId, taskId, data.title, data.description);

      if (response.data) {
        dispatch({ type: 'UPDATE_TASK', payload: response.data });
        dispatch({ type: 'SET_SHOW_EDIT_FORM', payload: false });
        dispatch({ type: 'SET_SELECTED_TASK', payload: null });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      console.error('Error updating task:', error);
      throw error;
    } finally {
      dispatch({ type: 'SET_UPDATING_TASK', payload: false });
    }
  }, [taskService]);

  const deleteTask = useCallback(async (acctId: string, taskId: string) => {
    try {
      dispatch({ type: 'SET_DELETING_TASK', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      await taskService.deleteTask(acctId, taskId);
      dispatch({ type: 'DELETE_TASK', payload: taskId });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      console.error('Error deleting task:', error);
      throw error;
    } finally {
      dispatch({ type: 'SET_DELETING_TASK', payload: false });
    }
  }, [taskService]);

  const searchTasks = useCallback(async (acctId: string, query: string) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
    // The loadTasks effect will handle the actual search
  }, []);

  const setFilters = useCallback((filters: Partial<TaskFilters>) => {
    dispatch({ type: 'SET_FILTERS', payload: filters });
  }, []);

  const setSearchQuery = useCallback((query: string) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
  }, []);

  const showCreateForm = useCallback(() => {
    dispatch({ type: 'SET_SHOW_CREATE_FORM', payload: true });
  }, []);

  const hideCreateForm = useCallback(() => {
    dispatch({ type: 'SET_SHOW_CREATE_FORM', payload: false });
  }, []);

  const showEditForm = useCallback((task: Task) => {
    dispatch({ type: 'SET_SELECTED_TASK', payload: task });
    dispatch({ type: 'SET_SHOW_EDIT_FORM', payload: true });
  }, []);

  const hideEditForm = useCallback(() => {
    dispatch({ type: 'SET_SHOW_EDIT_FORM', payload: false });
    dispatch({ type: 'SET_SELECTED_TASK', payload: null });
  }, []);

  const selectTask = useCallback((task: Task | null) => {
    dispatch({ type: 'SET_SELECTED_TASK', payload: task });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, []);

  const refreshTasks = useCallback(async (acctId: string) => {
    await loadTasks(acctId, 1, false);
  }, [loadTasks]);

  // Load initial tasks
  React.useEffect(() => {
    if (accountId) {
      loadTasks(accountId, 1, false);
    }
  }, [accountId, loadTasks]);

  // Reload tasks when filters or search change
  React.useEffect(() => {
    if (accountId) {
      const debounceTimer = setTimeout(() => {
        loadTasks(accountId, 1, false);
      }, 300); // Debounce search/filter changes

      return () => clearTimeout(debounceTimer);
    }
  }, [accountId, state.filters, state.searchQuery, loadTasks]);

  const actions = {
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
    searchTasks,
    setFilters,
    setSearchQuery,
    showCreateForm,
    hideCreateForm,
    showEditForm,
    hideEditForm,
    selectTask,
    clearError,
    refreshTasks,
  };

  return (
    <TaskContext.Provider value={{ state, actions }}>
      {children}
    </TaskContext.Provider>
  );
};

// Hook
export const useTaskContext = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTaskContext must be used within a TaskProvider');
  }
  return context;
};

export default TaskProvider;