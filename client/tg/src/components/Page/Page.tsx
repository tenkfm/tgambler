import { useNavigate } from 'react-router-dom';
import {
  hideBackButton,
  onBackButtonClick,
  showBackButton,
} from '@telegram-apps/sdk-react';
import {
  type PropsWithChildren,
  useEffect,
  type ReactNode,
  type CSSProperties,
} from 'react';
import { bem } from '@/css/bem.ts';

import './Page.css';

// Деструктурируем и функцию блока (b), и функцию элемента (e)
const [b, e] = bem('page');

interface PageProps {
  padding?: boolean;
  back?: boolean;
  header?: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export function Page({
  header,
  back = true,
  padding = true,
  children,
  className = '',
  style,
}: PropsWithChildren<PageProps>) {
  const navigate = useNavigate();

  useEffect(() => {
    if (back) {
      showBackButton();
      return onBackButtonClick(() => {
        navigate(-1);
      });
    }
    hideBackButton();
  }, [back, navigate]);

  // Используем b() для базового класса блока
  const rootClass = [ b(), className ].filter(Boolean).join(' ');

  return (
    <div className={rootClass} style={style}>
      {header}
      {padding ? <div className={e('body')}>{children}</div> : children}
    </div>
  );
}
