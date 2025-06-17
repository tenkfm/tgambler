import { type FC } from 'react';

import { Page } from '@/components/Page/Page';
import { Spinner } from '@/components/Spinner/Spinner.tsx';

import './SpinnerPage.css';

export const SpinnerPage: FC = () => {

  return (
    <Page
      padding={false}
    >
      <div className='spinner-page'>
      </div>
      <div className="content">
        <Spinner />
      </div>
    </Page>
  );
};
