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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@components/ui/select';
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
import { signUp } from '@apis/account';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const signupSchema = z
  .object({
    email: z.email({ message: '이메일 형식이 올바르지 않습니다.' }),
    password: z.string().min(8, { message: '비밀번호는 8자 이상이어야 합니다.' }),
    password_confirm: z.string().min(1, { message: '비밀번호 확인은 1자 이상이어야 합니다.' }),
    name: z.string().min(1, { message: '이름은 1자 이상이어야 합니다.' }),
    birth_date: z.string().min(1, { message: '생년월일은 1자 이상이어야 합니다.' }),
    gender: z.string().min(1, { message: '성별은 1자 이상이어야 합니다.' }),
    height: z
      .string()
      .refine((val) => Number(val) >= 50, { message: '키는 50 이상이어야 합니다.' }),
    weight: z
      .string()
      .refine((val) => Number(val) >= 20, { message: '몸무게는 20 이상이어야 합니다.' }),
  })
  .refine((data) => data.password === data.password_confirm, {
    path: ['password_confirm'],
    message: '비밀번호가 일치하지 않습니다.',
  });

type SignupSchemaType = z.infer<typeof signupSchema>;
function SignupPage() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const form = useForm<SignupSchemaType>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: '',
      password: '',
      password_confirm: '',
      name: '',
      birth_date: '',
      gender: '',
      height: '0',
      weight: '0',
    },
  });

  const onSubmit = useCallback(
    (data: SignupSchemaType) => {
      setIsLoading(true);
      signUp(
        data.email,
        data.password,
        data.name,
        data.birth_date,
        data.gender,
        data.height,
        data.weight,
      )
        .then(() => {
          toast.success('회원가입 성공');
          navigate('/login');
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
              <CardTitle>회원가입</CardTitle>
              <CardDescription>회원가입 해 주세요.</CardDescription>
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
                <FormField
                  control={form.control}
                  name='password_confirm'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>비밀번호 확인</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='password'
                          placeholder='비밀번호를 확인하세요'
                          autoComplete='current-password'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='name'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>이름</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder='이름을 입력하세요' autoComplete='name' />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='birth_date'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>생년월일</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='date'
                          placeholder='생년월일을 입력하세요'
                          autoComplete='birth-date'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='gender'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>성별</FormLabel>
                      <FormControl>
                        <Select
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                          {...field}
                          autoComplete='gender'
                        >
                          <SelectTrigger>
                            <SelectValue placeholder='성별을 선택하세요' />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value='male'>남자</SelectItem>
                            <SelectItem value='female'>여자</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='height'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>키</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='number'
                          placeholder='키를 입력하세요'
                          autoComplete='height'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name='weight'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>몸무게</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type='number'
                          placeholder='몸무게를 입력하세요'
                          autoComplete='weight'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
              <CardFooter>
                <Button type='submit' className='w-full' disabled={isLoading}>
                  {isLoading ? '회원가입 중...' : '회원가입'}
                </Button>
              </CardFooter>
            </form>
          </Form>
        </Card>
      </div>
    </main>
  );
}

export default SignupPage;
