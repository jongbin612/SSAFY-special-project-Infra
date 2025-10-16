import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { type User } from '@/types/accountsType';
import { me } from '@apis/account';

interface UserState {
  user: User | null;
  isLogin: boolean;
  token: string | null;
  setIsLogin: (isLogin: boolean) => void;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  login: (user: User, token: string) => void;
  checkLogin: () => Promise<string | null>;
}

const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      isLogin: false,
      token: null,
      setUser: (user: User) => set({ user }),
      setToken: (token: string) => set({ token }),
      setIsLogin: (isLogin: boolean) => set({ isLogin }),
      login: (user: User, token: string) => set({ user, token, isLogin: true }),
      logout: () => set({ user: null, token: null, isLogin: false }),
      checkLogin: async () => {
        const user = await me();
        if (user) {
          set({ user, isLogin: true });
        }
        return user && get().token;
      },
    }),
    {
      name: 'user',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isLogin: state.isLogin,
      }),
    },
  ),
);

export default useUserStore;
