import { DayButton, DayPicker, type DayPickerProps } from 'react-day-picker';
import 'react-day-picker/style.css';

// Adapts the Neobrutalism calendar recipe to Smolink's token CSS.
export function Calendar(props: DayPickerProps) {
  return (
    <DayPicker
      showOutsideDays
      className="calendar"
      components={{
        DayButton: ({ day, ...buttonProps }) => (
          <DayButton
            {...buttonProps}
            day={day}
            data-day={day.date.toLocaleDateString('en-CA')}
          />
        ),
      }}
      {...props}
    />
  );
}
