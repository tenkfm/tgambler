import { useState } from 'react';
import { invoice } from '@telegram-apps/sdk';
import { Banner, Button, Section, Cell, List } from '@telegram-apps/telegram-ui';

import {
  initDataRaw as _initDataRaw,
  initDataState as _initDataState,
  useSignal,
} from '@telegram-apps/sdk-react';

import type { FC } from 'react';
import axios from 'axios';

import { Link } from '@/components/Link/Link.tsx';
import { Page } from '@/components/Page.tsx';
import { Header } from '@/components/Header/Header';

import banner from './banner.jpg';

export const IndexPage: FC = () => {
  const initDataState = useSignal(_initDataState);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const payByTelegramStar = () => {
    setIsLoading(true);
    setMessage(null);

    axios.post(
      "https://fuzzy-waddle-rrqjpx67xrcgjw-8000.app.github.dev/invoice",
      {
        th_id: initDataState?.user?.id || 0,
        amount: 10
      }
    )
    .then(response => {
      const url = response.data.url;

      if (invoice.open.isAvailable()) {
        invoice.open(url, 'url')
          .then(status => {
            if (status === 'paid') {
              setMessage('🎉 Payment completed!');
            } else {
              setMessage('❌ Payment was cancelled or failed.');
            }
          })
          .catch(() => {
            setMessage('⚠️ Error during payment.');
          })
          .finally(() => {
            setIsLoading(false);
          });
      } else {
        setMessage('ℹ️ Payments not supported in this client.');
        setIsLoading(false);
      }
    })
    .catch(() => {
      setMessage('❌ Failed to initiate payment.');
      setIsLoading(false);
    });
  };

  return (
    <Page back={false}>
      <Header />
      
      <Banner
        type="inline"
        background={<img alt="Free Spins Banner" src={banner} style={{ width: '100%', filter: 'brightness(0.4)' }} />}
        header="Buy a Good Luck for only 10 ★"
        subheader="You can get up to 50 free spins every day!"
      >
        <Button mode="white" size="s" loading={isLoading} onClick={payByTelegramStar}>
          Buy a Good Luck
        </Button>
      </Banner>

      {message && (
        <div style={{ textAlign: 'center', margin: '16px', fontSize: '16px' }}>
          {message}
        </div>
      )}

      <List>
        <Section header="Application Launch Data">
          <Link to="/init-data">
            <Cell subtitle="User data, chat information, technical data">Init Data</Cell>
          </Link>
          <Link to="/launch-params">
            <Cell subtitle="Platform identifier, Mini Apps version, etc.">Launch Parameters</Cell>
          </Link>
          <Link to="/theme-params">
            <Cell subtitle="Telegram application palette information">Theme Parameters</Cell>
          </Link>
        </Section>
      </List>
    </Page>
  );
};
