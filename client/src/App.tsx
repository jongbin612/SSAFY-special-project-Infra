import { BrowserRouter } from 'react-router-dom';
import Router from '@pages/Router';
import { Toaster } from '@components/ui/sonner';

const App = () => {
  return (
    <>
      <BrowserRouter>
        <Router />
      </BrowserRouter>
      <Toaster richColors closeButton position='top-center' duration={2000} />
    </>
  );
};

export default App;
