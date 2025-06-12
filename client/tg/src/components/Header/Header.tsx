import type { FC } from 'react';
import { Avatar, Button, Headline, Caption } from '@telegram-apps/telegram-ui';
import { Link } from '@/components/Link/Link.tsx';

import {
  initDataRaw as _initDataRaw,
  initDataState as _initDataState,
  useSignal,
} from '@telegram-apps/sdk-react';
import { bem } from '@/css/bem.ts';

import tonSvg from './ton.svg';
import './Header.css';

const [, e] = bem('header');

export const Header: FC = () => {
  const initDataState = useSignal(_initDataState);

  return (
    <div className={e('container')}>
        <div className={e('left')}>
            <Avatar src={initDataState?.user?.photo_url} size={40} />
            <Headline weight="2" className={e('name')}>
            {initDataState?.user?.first_name}
            </Headline>
        </div>

        <div className={e('right')}>
            <Link to="/ton-connect">
                <Button size="s" mode="outline">Connect Wallet</Button>
            </Link>
            
            <Caption weight="1">0.00</Caption>

            <div className={e('icon')}>
                <img src={tonSvg} alt="TON" />
            </div>
        </div>
    </div>
  );
};
