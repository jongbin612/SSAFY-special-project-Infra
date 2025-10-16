import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@components/ui/card';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@components/ui/form';
import { Input } from '@components/ui/input';
import { Button } from '@components/ui/button';
import { useCallback, useState } from 'react';
import { login } from '@apis/account';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import useUserStore from '@/stores/userStore';

const loginSchema = z.object({
  email: z.email({ message: '이메일 형식이 올바르지 않습니다.' }),
  password: z.string().min(8, { message: '비밀번호는 8자 이상이어야 합니다.' }),
});

type LoginSchemaType = z.infer<typeof loginSchema>;

function Login() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const form = useForm<LoginSchemaType>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = useCallback(
    (data: LoginSchemaType) => {
      setIsLoading(true);
      login(data.email, data.password)
        .then((res) => {
          toast.success('로그인 성공');
          useUserStore.getState().login(res.user, res.access_token);
          navigate('/');
        })
        .finally(() => {
          setIsLoading(false);
        });
    },
    [navigate],
  );

  return (
    <main className='min-h-screen max-w-[480px] min-w-[375px] w-full mx-auto bg-gray-50 flex flex-col'>
      <div className='flex flex-col justify-center gap-8 items-center h-full flex-1 px-4'>
        <Card className='w-full max-w-md shadow-lg'>
          <CardHeader>
            <div className='flex flex-col gap-2 justify-center items-center'>
              <CardTitle>로그인</CardTitle>
              <CardDescription>로그인 해 주세요.</CardDescription>
            </div>
          </CardHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
              <CardContent className='space-y-4'>
                <FormField
                  control={form.control}
                  name='email'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>이메일</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='email'
                          placeholder='이메일을 입력하세요'
                          autoComplete='email'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='password'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>비밀번호</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='password'
                          placeholder='비밀번호를 입력하세요'
                          autoComplete='current-password'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
              <CardFooter>
                <Button type='submit' className='w-full' disabled={isLoading}>
                  {isLoading ? '로그인 중...' : '로그인'}
                </Button>
              </CardFooter>
            </form>
          </Form>
        </Card>
        <Button
          className='w-full'
          onClick={() => {
            navigate('/signup');
          }}
        >
          회원가입
        </Button>
      </div>
    </main>
  );
}

export default Login;
