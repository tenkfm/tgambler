import { type FC } from 'react';
import { useState } from 'react';

import { Page } from '@/components/Page.tsx';

import RoulettePro from 'react-roulette-pro';
import { Spinner } from '@/components/Spinner/Spinner.tsx';

export const SpinnerPage: FC = () => {

  return (
    <Page>
      <Spinner />

    </Page>
  );
};
