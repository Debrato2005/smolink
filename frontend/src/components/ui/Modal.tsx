import { Dialog } from '@base-ui/react/dialog';
import type { ReactNode } from 'react';
import { Icon } from './Icon';
export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="modal-backdrop" />
        <Dialog.Viewport className="modal-viewport">
          <Dialog.Popup className="modal">
            <div className="modal-heading">
              <Dialog.Title>{title}</Dialog.Title>
              <Dialog.Close className="icon-button" aria-label="Close dialog">
                <Icon name="close" />
              </Dialog.Close>
            </div>
            <Dialog.Description className="muted">
              {description}
            </Dialog.Description>
            {children}
          </Dialog.Popup>
        </Dialog.Viewport>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
