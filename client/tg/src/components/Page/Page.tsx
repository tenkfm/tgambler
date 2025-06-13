import { useNavigate } from 'react-router-dom';
import { hideBackButton, onBackButtonClick, showBackButton } from '@telegram-apps/sdk-react';
import { type PropsWithChildren, useEffect, type ReactNode } from 'react';
import { bem } from '@/css/bem.ts';

import './Page.css';
const [, e] = bem('page');

interface PageProps {
  /**
   * True if the page should have padding.
   */
  padding?: boolean;
  /**
   * True if it is allowed to go back from this page.
   */
  back?: boolean;
  /**
   * Optional header content to render above the page body.
   */
  header?: ReactNode;
}

export function Page({ header, back = true, padding = true, children }: PropsWithChildren<PageProps>) {
  const navigate = useNavigate();

  useEffect(() => {
    if (back) {
      showBackButton();
      return onBackButtonClick(() => {
        navigate(-1);
      });
    }
    hideBackButton();
  }, [back]);

  return (
    <div>
      {header}
      {padding ? <div className={e('body')}>{children}</div> : children}
    </div>
  );
}
