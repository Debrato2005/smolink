import type { CSSProperties } from 'react';
import { createPortal } from 'react-dom';

export function CopyConfetti({ x, y }: { x: number; y: number }) {
  return createPortal(
    <div
      className="copy-confetti"
      aria-hidden="true"
      style={{ '--burst-x': `${x}px`, '--burst-y': `${y}px` } as CSSProperties}
    >
      {Array.from({ length: 24 }, (_, index) => {
        const angle = (Math.PI * (index + 0.5)) / 24;
        const distance = 65 + (index % 4) * 22;
        return (
          <i
            key={index}
            style={
              {
                '--confetti-x': `${Math.cos(angle) * distance}px`,
                '--confetti-y': `${-Math.sin(angle) * distance}px`,
                '--confetti-spin': `${(index % 2 ? 1 : -1) * (180 + index * 15)}deg`,
              } as CSSProperties
            }
          />
        );
      })}
    </div>,
    document.body,
  );
}
