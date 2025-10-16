import { Dropzone, DropzoneContent, DropzoneEmptyState } from '@/components/ui/shadcn-io/dropzone';
import { toast } from 'sonner';
import { AspectRatio } from '@radix-ui/react-aspect-ratio';
import Image from '@/components/common/Image';

interface ImageInputProps {
  setFiles: React.Dispatch<React.SetStateAction<File[]>>;
  files: File[];
  className?: string;
}

function ImageInput({ setFiles, files, className }: ImageInputProps) {
  const handleDrop = (files: File[]) => {
    setFiles(files);
  };
  return (
    <Dropzone
      maxSize={1024 * 1024 * 10}
      minSize={1024}
      accept={{ 'image/*': [] }}
      onDrop={handleDrop}
      onError={(err) => {
        toast.error(err.message);
      }}
      src={files}
      className={className}
    >
      <DropzoneEmptyState />
      <DropzoneContent>
        {files && files.length > 0 && (
          <AspectRatio ratio={16 / 9}>
            <Image
              src={URL.createObjectURL(files[0])}
              alt='image'
              className='w-full h-full object-contain'
            />
          </AspectRatio>
        )}
      </DropzoneContent>
    </Dropzone>
  );
}
export default ImageInput;
