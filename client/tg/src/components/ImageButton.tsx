import React, { FC, ButtonHTMLAttributes } from 'react';

interface ImageButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** URL of the image to show as the button background */
  image: string;
  /** Any children to render on top (e.g. label) */
  children?: React.ReactNode;
}

export const ImageButton: FC<ImageButtonProps> = ({
  image,
  children,
  style,
  ...buttonProps
}) => {
  return (
    <button
      {...buttonProps}
      style={{
        width: '100%',
        height: '200px',
        padding: 0,
        margin: 0,
        border: '6px solid rgba(255, 255, 255, 0.5)',  // увеличенная полупрозрачная рамка
        borderRadius: '30px',                          // скруглённые углы (30px)
        overflow: 'hidden',                             // обрезаем всё, что выходит за скругления
        background: `url(${image}) center center / cover no-repeat`,
        cursor: 'pointer',
        // boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',      // лёгкая тень для глубины
        ...style,
      }}
    >
      {children && (
        <span
          style={{
            position: 'relative',
            display: 'inline-block',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '100%',
            textAlign: 'center',
            color: '#fff',
            textShadow: '0 1px 3px rgba(0,0,0,0.6)',
            pointerEvents: 'none', // текст не блокирует клик по кнопке
          }}
        >
          {children}
        </span>
      )}
    </button>
  );
};