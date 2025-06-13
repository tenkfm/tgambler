import type { FC } from 'react';
import { useState } from 'react';

import RoulettePro from 'react-roulette-pro';
import 'react-roulette-pro/dist/index.css';
import { Header } from '@/components/Header/Header';
import { Button } from '@telegram-apps/telegram-ui';

type Prize = { image: string };

const prizes = [
  {
    image: 'https://i.ibb.co/6Z6Xm9d/good-1.png',
  },
  {
    image: 'https://i.ibb.co/T1M05LR/good-2.png',
  },
  {
    image: 'https://i.ibb.co/Qbm8cNL/good-3.png',
  },
  {
    image: 'https://i.ibb.co/5Tpfs6W/good-4.png',
  },
  {
    image: 'https://i.ibb.co/64k8D1c/good-5.png',
  },
];

const winPrizeIndex = 4;

const reproductionArray = (array: Prize[], length: number): Prize[] =>
  Array.from({ length }, () => array[Math.floor(Math.random() * array.length)]);

const reproducedPrizeList = [
  ...prizes,
  ...reproductionArray(prizes, prizes.length * 3),
  ...prizes,
  ...reproductionArray(prizes, prizes.length),
];

const generateId = () =>
  `${Date.now().toString(36)}-${Math.random().toString(36).substring(2)}`;

const prizeList = reproducedPrizeList.map((prize) => ({
  ...prize,
  id: typeof crypto.randomUUID === 'function' ? crypto.randomUUID() : generateId(),
}));

export const Spinner: FC = () => {
  const [start, setStart] = useState(false);

  const prizeIndex = prizes.length * 4 + winPrizeIndex;

  const handleStart = () => {
    setStart((prevState) => !prevState);
  };

  const handlePrizeDefined = () => {
    console.log('🥳 Prize defined! 🥳');
  };

  return (
    <>
        <RoulettePro
            prizes={prizeList}
            prizeIndex={prizeIndex}
            start={start}
            onPrizeDefined={handlePrizeDefined}
            spinningTime={10}
        />

        <Button mode="outline" size="m" style={{ margin: '16px auto', display: 'block' }} onClick={handleStart}>
            🍀 Spin 🍀
        </Button>
    </>
  );
};