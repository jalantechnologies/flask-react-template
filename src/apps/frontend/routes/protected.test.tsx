import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  MemoryRouter,
  RouteObject,
  useLocation,
  useRoutes,
} from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AccountProvider, AuthProvider } from 'frontend/contexts';
import { protectedRoutes } from 'frontend/routes/protected';
import { publicRoutes } from 'frontend/routes/public';

const { get, post } = vi.hoisted(() => {
  window.Config = { authenticationMechanism: 'EMAIL' };

  return { get: vi.fn(), post: vi.fn() };
});

vi.mock('axios', () => ({
  default: { create: () => ({ get, post }) },
}));

const LocationProbe: React.FC = () => {
  const { pathname } = useLocation();

  return <span data-testid="pathname">{pathname}</span>;
};

const RouteSet: React.FC<{ routeSet: RouteObject[] }> = ({ routeSet }) =>
  useRoutes(routeSet);

const visit = (routeSet: RouteObject[], path: string) =>
  render(
    <AuthProvider>
      <AccountProvider>
        <MemoryRouter initialEntries={[path]}>
          <LocationProbe />
          <RouteSet routeSet={routeSet} />
        </MemoryRouter>
      </AccountProvider>
    </AuthProvider>,
  );

const signIn = () => {
  localStorage.setItem(
    'access-token',
    JSON.stringify({
      account_id: 'acc-1',
      token: 'jwt-123',
      expires_at: '2999-01-01T00:00:00Z',
    }),
  );
};

beforeEach(() => {
  localStorage.clear();
  get.mockResolvedValue({
    data: {
      id: 'acc-1',
      first_name: 'Ada',
      last_name: 'Lovelace',
      username: 'ada@example.com',
    },
  });
});

describe('protected routes', () => {
  it('sends a signed in user visiting the login path to the dashboard', async () => {
    signIn();

    visit(protectedRoutes as RouteObject[], '/login');

    expect(await screen.findByTestId('dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('pathname')).toHaveTextContent('/');
  });

  it('sends a signed in user visiting the signup path to the dashboard', async () => {
    signIn();

    visit(protectedRoutes as RouteObject[], '/signup');

    expect(await screen.findByTestId('dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('pathname')).toHaveTextContent('/');
  });

  it('still renders the not found page for an unknown path', async () => {
    signIn();

    visit(protectedRoutes as RouteObject[], '/definitely-not-a-route');

    expect(await screen.findByTestId('notFoundContainer')).toBeInTheDocument();
  });
});

describe('public routes', () => {
  it('still shows the login form to a signed out user', async () => {
    visit(publicRoutes as RouteObject[], '/login');

    expect(
      await screen.findByRole('heading', { name: 'Log In' }),
    ).toBeInTheDocument();
  });

  it('still shows the signup form to a signed out user', async () => {
    visit(publicRoutes as RouteObject[], '/signup');

    expect(
      await screen.findByRole('heading', { name: 'Sign Up' }),
    ).toBeInTheDocument();
  });
});
