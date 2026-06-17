import SegmentedControl from '../ui/SegmentedControl';

interface IntensityOption {
  label: string;
  value: string;
}

interface IntensitySelectorProps {
  value: string;
  onChange: (value: string) => void;
  options?: IntensityOption[];
  label?: string;
}

const DEFAULT_OPTIONS: IntensityOption[] = [
  { label: 'Light', value: 'light' },
  { label: 'Medium', value: 'medium' },
  { label: 'Heavy', value: 'heavy' },
];

export default function IntensitySelector({
  value,
  onChange,
  options = DEFAULT_OPTIONS,
  label = 'Intensity',
}: IntensitySelectorProps) {
  return (
    <div className="field">
      <label className="field-label">{label}</label>
      <SegmentedControl
        options={options}
        value={value}
        onChange={onChange}
        ariaLabel={label}
      />
    </div>
  );
}
