import { useCallback, useState, useRef } from 'react';
import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';

const elevenlabs = new ElevenLabsClient({
  apiKey: import.meta.env.VITE_ELEVENLABS_API_KEY,
});

interface UseTextToSpeechOptions {
  modelId?: string; // 사용할 모델 ID (기본값: eleven_flash_v2_5)
  voiceId: string; // ElevenLabs의 음성 ID
  stability?: number; // 음성 안정성 (0~1)
  similarityBoost?: number; // 원본 음성과의 유사도 (0~1)
  styleExaggeration?: number; // 스타일 과장도
  useSpeakerBoost?: boolean; // 스피커 부스트 사용 여부
  playbackRate?: number; // 재생 속도
  onStart?: () => void; // 재생 시작 콜백
  onEnd?: () => void; // 재생 종료 콜백
  onError?: (error: Error) => void; // 에러 처리 콜백
}

export function useTextToSpeech(options: UseTextToSpeechOptions) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const stopSpeech = useCallback(() => {
    // 진행 중인 API 요청 취소
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    // 오디오 재생 중지
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      setAudioElement(null);
    }

    setIsPlaying(false);
    options.onEnd?.();
  }, [audioElement, options]);

  const speakText = useCallback(
    async (text: string) => {
      // 이미 재생 중이면 중지
      if (isPlaying) {
        stopSpeech();
        return;
      }

      // 빈 텍스트 체크
      if (!text.trim()) {
        options.onError?.(new Error('텍스트가 비어있습니다.'));
        return;
      }

      try {
        setIsPlaying(true);
        options.onStart?.();

        // AbortController 생성
        abortControllerRef.current = new AbortController();

        // ElevenLabs API 호출 - 더 간단한 방식 사용
        const audioResponse = await elevenlabs.textToSpeech.convert(options.voiceId, {
          text,
          modelId: options.modelId || 'eleven_flash_v2_5',
          voiceSettings: {
            stability: options.stability ?? 0.5,
            similarityBoost: options.similarityBoost ?? 0.8,
            style: options.styleExaggeration ?? 0.0,
            useSpeakerBoost: options.useSpeakerBoost ?? true,
          },
        });

        // 응답이 취소되었는지 확인
        if (abortControllerRef.current?.signal.aborted) {
          setIsPlaying(false);
          return;
        }

        // ReadableStream을 ArrayBuffer로 변환
        const reader = audioResponse.getReader();
        const chunks: Uint8Array[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
        }

        // 모든 청크를 하나의 Uint8Array로 합치기
        const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
        const audioBuffer = new Uint8Array(totalLength);
        let offset = 0;

        for (const chunk of chunks) {
          audioBuffer.set(chunk, offset);
          offset += chunk.length;
        }

        // Uint8Array를 Blob으로 변환
        const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);

        // 오디오 엘리먼트 생성 및 설정
        const audio = new Audio(audioUrl);
        setAudioElement(audio);

        // 재생 속도 설정
        if (options.playbackRate) {
          audio.playbackRate = options.playbackRate;
        }

        // 오디오 이벤트 핸들러 설정
        const handleAudioEnd = () => {
          setIsPlaying(false);
          setAudioElement(null);
          URL.revokeObjectURL(audioUrl); // 메모리 정리
          options.onEnd?.();
        };

        const handleAudioError = () => {
          setIsPlaying(false);
          setAudioElement(null);
          URL.revokeObjectURL(audioUrl); // 메모리 정리
          options.onError?.(new Error('오디오 재생에 실패했습니다.'));
        };

        audio.addEventListener('ended', handleAudioEnd);
        audio.addEventListener('error', handleAudioError);

        // 오디오 재생 시작
        await audio.play();
      } catch (error) {
        setIsPlaying(false);
        setAudioElement(null);

        // AbortError는 의도적인 취소이므로 에러로 처리하지 않음
        if (error instanceof Error && error.name === 'AbortError') {
          return;
        }

        const errorMessage = error instanceof Error ? error.message : '음성 생성에 실패했습니다.';
        options.onError?.(new Error(errorMessage));
      } finally {
        abortControllerRef.current = null;
      }
    },
    [isPlaying, options, stopSpeech],
  );

  return {
    isPlaying,
    audioElement,
    stopSpeech,
    speakText,
  };
}
