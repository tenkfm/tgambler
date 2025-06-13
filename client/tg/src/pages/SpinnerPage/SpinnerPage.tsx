import { type FC } from 'react';

import { Page } from '@/components/Page/Page';
import { Spinner } from '@/components/Spinner/Spinner.tsx';
import { Header } from '@/components/Header/Header';

export const SpinnerPage: FC = () => {

  return (
    <Page padding={false} header={ <Header /> }>
      <Spinner />
    </Page>
  );
};
