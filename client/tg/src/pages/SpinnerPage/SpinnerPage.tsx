import { type FC } from 'react';

import { Page } from '@/components/Page.tsx';
import { Spinner } from '@/components/Spinner/Spinner.tsx';

export const SpinnerPage: FC = () => {

  return (
    <Page>
      <Spinner />
    </Page>
  );
};
