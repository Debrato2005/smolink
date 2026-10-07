// Adapted from neobrutalism.dev/r/button.json (MIT). See THIRD_PARTY_NOTICES.md.
// Preserve Base UI behavior. Smolink token CSS replaces the Tailwind/cva skin.
import { Button as ButtonPrimitive } from '@base-ui/react/button';
import type { ComponentProps } from 'react';

export function Button({
  className,
  ...props
}: ComponentProps<typeof ButtonPrimitive>) {
  return (
    <ButtonPrimitive
      className={`button ${typeof className === 'string' ? className : ''}`}
      {...props}
    />
  );
}
