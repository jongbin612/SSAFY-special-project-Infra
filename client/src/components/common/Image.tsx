import { useState } from 'react';
import notFound from '@/assets/notFound.png';

interface ImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  className?: string;
}

function Image({ src, alt, className, ...restProps }: ImageProps) {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError && currentSrc !== notFound) {
      setHasError(true);
      setCurrentSrc(notFound);
    }
  };

  return (
    <img src={currentSrc} alt={alt} className={className} onError={handleError} {...restProps} />
  );
}

export default Image;
