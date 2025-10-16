import { useRoutes } from 'react-router-dom';
import Layout from '@pages/Layout';
import MainPage from '@pages/Home';
import ExercisePage from '@pages/ExercisePage';
import LoginPage from '@pages/Login';
import NotFoundPage from '@pages/NotFoundPage';
import MyPage from '@pages/MyPage';
import ExerciseCoachPage from '@pages/ExerciseCoachPage';
import ExerciseDetail from '@pages/ExerciseDetail';
import ExerciseCoachResultPage from '@pages/ExerciseCoachResultPage';
import UserBodyAnalysisPage from '@pages/UserBodyAnalysisPage';
import SignupPage from '@pages/SignupPage';

export default function Router() {
  return useRoutes([
    {
      path: '/',
      element: <Layout />,
      children: [
        {
          path: '/',
          element: <MainPage />,
        },
        {
          path: '/exercise',
          element: <ExercisePage />,
        },
        {
          path: '/user/body_analysis',
          element: <UserBodyAnalysisPage />,
        },
        {
          path: '/exercise/:exerciseId',
          element: <ExerciseDetail />,
        },
        {
          path: '/my_page',
          element: <MyPage />,
        },
      ],
    },
    {
      path: '/login',
      element: <LoginPage />,
    },
    {
      path: '/signup',
      element: <SignupPage />,
    },
    {
      path: '/exercise/coach/:sessionId',
      element: <ExerciseCoachPage />,
    },
    {
      path: '/exercise/coach/:sessionId/result',
      element: <ExerciseCoachResultPage />,
    },
    {
      path: '*',
      element: <NotFoundPage />,
    },
  ]);
}
