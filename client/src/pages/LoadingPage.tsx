function LoadingPage({ message }: { message?: string }) {
  return (
    <div className='absolute inset-0 bg-accent bg-opacity-50 flex items-center justify-center z-40'>
      <div className='flex flex-col items-center justify-center'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-chart-2 mx-auto mb-4'></div>
        <p>{message || '로딩중...'}</p>
      </div>
    </div>
  );
}

export default LoadingPage;
