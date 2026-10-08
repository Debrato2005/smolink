import { Popover } from '@base-ui/react/popover';
import { lazy, Suspense, useState } from 'react';
import { Field } from './Field';
import { Icon } from './Icon';
import { Button } from './Button';
import { Skeleton } from './Feedback';
import { localDateInput } from '../../lib/validation';

const Calendar = lazy(() =>
  import('./Calendar').then((module) => ({ default: module.Calendar })),
);

export function DatePicker({
  id,
  value,
  onChange,
  disabled = false,
  error,
  hint,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: string | undefined;
  hint: string;
}) {
  const [open, setOpen] = useState(false);
  const date = value ? new Date(value) : undefined;
  const selected = date && !Number.isNaN(date.getTime()) ? date : undefined;
  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <div className="field date-picker-field">
        <label htmlFor={id}>Expiry date and time</label>
        <Popover.Trigger
          id={id}
          name="expires_at"
          className="date-picker-trigger"
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={`${id}-hint${error ? ` ${id}-error` : ''}`}
        >
          <Icon name="calendar" />
          <span>
            {selected
              ? selected.toLocaleString('en', {
                  dateStyle: 'medium',
                  timeStyle: 'short',
                })
              : 'Choose a date and time'}
          </span>
          <Icon name="chevron" size={16} />
        </Popover.Trigger>
        {error && (
          <p id={`${id}-error`} className="field-error">
            <Icon name="alert" size={16} />
            {error}
          </p>
        )}
        <p id={`${id}-hint`} className="field-help">
          {hint}
        </p>
      </div>
      <Popover.Portal>
        <Popover.Positioner
          className="control-positioner"
          sideOffset={8}
          align="end"
        >
          <Popover.Popup className="control-popup calendar-popup">
            <Popover.Title className="sr-only">
              Choose expiry date
            </Popover.Title>
            <Suspense
              fallback={
                <div role="status" aria-label="Loading calendar…">
                  <Skeleton className="calendar-skeleton" />
                </div>
              }
            >
              <Calendar
                mode="single"
                selected={selected}
                defaultMonth={selected ?? new Date()}
                autoFocus
                disabled={{ before: new Date(new Date().setHours(0, 0, 0, 0)) }}
                onSelect={(next) => {
                  if (!next) return;
                  const day = localDateInput(next.toISOString()).slice(0, 10);
                  onChange(`${day}T${value.slice(11, 16) || '12:00'}`);
                }}
              />
            </Suspense>
            <div className="calendar-date-time">
              <Field
                id={`${id}-date`}
                label="Date"
                placeholder="YYYY-MM-DD"
                value={value.slice(0, 10)}
                onChange={(event) =>
                  onChange(
                    event.target.value
                      ? `${event.target.value}T${value.slice(11, 16) || '12:00'}`
                      : '',
                  )
                }
              />
              <Field
                id={`${id}-time`}
                label="Time"
                type="time"
                value={value.slice(11, 16) || '12:00'}
                onChange={(event) => {
                  const day =
                    value.slice(0, 10) ||
                    localDateInput(new Date().toISOString()).slice(0, 10);
                  onChange(`${day}T${event.target.value}`);
                }}
              />
            </div>
            <p className="field-help">{hint}</p>
            <div className="calendar-actions">
              <Button
                className="button-secondary button-small"
                onClick={() => {
                  onChange('');
                  setOpen(false);
                }}
              >
                Clear
              </Button>
              <Button className="button-small" onClick={() => setOpen(false)}>
                Done <Icon name="check" size={16} />
              </Button>
            </div>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
