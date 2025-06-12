import { Banner, Button, Section, Cell, List } from '@telegram-apps/telegram-ui';
import type { FC } from 'react';

import { Link } from '@/components/Link/Link.tsx';
import { Page } from '@/components/Page.tsx';

import banner from './banner.jpg';
import { Header } from '@/components/Header/Header';

export const IndexPage: FC = () => {
  return (
    <Page back={false}>

      <Header />

      <Banner
      type="inline"
      background={<img alt="Free Spins Banner" src={banner} style={{width: '100%', filter: 'brightness(0.4)'}}/>}
      header="Free Spins 🍀"
      subheader="You can get up to 50 free spins every day!"
    >
      <Button mode="white" size="s" > Try it out </Button>
    </Banner>  

      <List>
        <Section
          header="Application Launch Data"
        >
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
