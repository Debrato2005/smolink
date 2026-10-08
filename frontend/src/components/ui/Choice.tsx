import { Select } from '@base-ui/react/select';
import { Combobox } from '@base-ui/react/combobox';
import { Icon } from './Icon';

type ChoiceProps = {
  id: string;
  label: string;
  value: string;
  items: { value: string; label: string }[];
  onChange: (value: string) => void;
};

// The Neobrutalism select composition uses Base UI with local token CSS.
export function Dropdown({ id, label, value, items, onChange }: ChoiceProps) {
  return (
    <div className="filter-field">
      <label htmlFor={id}>{label}</label>
      <Select.Root
        items={items}
        value={value}
        onValueChange={(next) => {
          if (next !== null) onChange(next);
        }}
      >
        <Select.Trigger id={id} className="choice-trigger">
          <Select.Value />
          <Select.Icon>
            <Icon name="chevron" size={18} />
          </Select.Icon>
        </Select.Trigger>
        <Select.Portal>
          <Select.Positioner
            className="control-positioner"
            sideOffset={8}
            alignItemWithTrigger={false}
          >
            <Select.Popup className="control-popup">
              <Select.List>
                {items.map((item) => (
                  <Select.Item
                    key={item.value}
                    value={item.value}
                    className="choice-item"
                  >
                    <Select.ItemText>{item.label}</Select.ItemText>
                    <Select.ItemIndicator>
                      <Icon name="check" size={18} />
                    </Select.ItemIndicator>
                  </Select.Item>
                ))}
              </Select.List>
            </Select.Popup>
          </Select.Positioner>
        </Select.Portal>
      </Select.Root>
    </div>
  );
}

export function SearchableChoice({
  id,
  label,
  value,
  items,
  onChange,
}: ChoiceProps) {
  const selected = items.find((item) => item.value === value) ?? items[0]!;
  return (
    <div className="filter-field">
      <label htmlFor={id}>{label}</label>
      <Combobox.Root
        items={items}
        value={selected}
        onValueChange={(next) => {
          if (next) onChange(next.value);
        }}
      >
        <Combobox.Trigger id={id} className="choice-trigger">
          <Combobox.Value />
          <Icon name="chevron" size={18} />
        </Combobox.Trigger>
        <Combobox.Portal>
          <Combobox.Positioner className="control-positioner" sideOffset={8}>
            <Combobox.Popup
              className="control-popup"
              aria-label={`${label} options`}
            >
              <div className="choice-search">
                <Icon name="search" size={18} />
                <Combobox.Input
                  aria-label={`Search ${label.toLowerCase()} options`}
                  placeholder="Find an option…"
                />
              </div>
              <Combobox.Empty className="choice-empty">
                No matching options.
              </Combobox.Empty>
              <Combobox.List>
                {(item: ChoiceProps['items'][number]) => (
                  <Combobox.Item
                    key={item.value}
                    value={item}
                    className="choice-item"
                  >
                    {item.label}
                    <Combobox.ItemIndicator>
                      <Icon name="check" size={18} />
                    </Combobox.ItemIndicator>
                  </Combobox.Item>
                )}
              </Combobox.List>
            </Combobox.Popup>
          </Combobox.Positioner>
        </Combobox.Portal>
      </Combobox.Root>
    </div>
  );
}
