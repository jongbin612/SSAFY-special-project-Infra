import { useEffect, useState } from 'react';
import { toast } from 'sonner';

interface UseSocketProps {
  url: string;
  socketRef: React.RefObject<WebSocket | null>;
  autoConnect?: boolean;
}

const useSocket = ({ url, socketRef, autoConnect = true }: UseSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!url || !autoConnect) return;

    try {
      socketRef.current = new WebSocket(import.meta.env.VITE_SOCKET_URL + url);

      // 연결 상태 이벤트 리스너
      socketRef.current.onopen = () => {
        toast.success('운동서버와 연결에 성공했습니다.');
        setIsConnected(true);
        setError(null);
      };

      socketRef.current.onclose = () => {
        toast.error('운동서버와 연결을 종료합니다.');
        setIsConnected(false);
      };

      socketRef.current.onerror = () => {
        toast.error('운동서버와 연결에 실패했습니다. 페이지를 새로고침 해 주세요.');
        // const err = new Error('운동서버와 연결에 실패했습니다.');
        // setError(err);
        setIsConnected(false);
      };

      return () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.close();
        }
        setIsConnected(false);
        setError(null);
      };
    } catch (err) {
      toast.error('운동서버와 연결에 실패했습니다.:', { description: (err as Error).message });
      setError(err as Error);
    }
  }, [url, socketRef, autoConnect]);

  const sendMessage = (message: string | object) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      socketRef.current.send(messageStr);
    } else {
      toast.error('운동서버와 연결에 실패했습니다.');
    }
  };

  return {
    isConnected,
    error,
    sendMessage,
  };
};

export default useSocket;
